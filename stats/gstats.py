#!/usr/bin/env python3
"""
Gatling Statistics Calculator

Calculate statistics like percentiles from Gatling simulation.csv files.
"""

import argparse
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import NamedTuple

import argcomplete
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from tdigest import TDigest

percentile_range_colors = {
    "0-50th": "#2E86AB",  # Blue
    "50th-75th": "#A23B72",  # Purple
    "75th-95th": "#F18F01",  # Orange
    "95th-99th": "#C73E1D",  # Red
    "99th-max": "#8B0000",  # Dark red
}

percentile_line_colors = {
    "50th": "#2E86AB",  # Blue
    "75th": "#A23B72",  # Purple
    "95th": "#F18F01",  # Orange
    "99th": "#C73E1D",  # Red
    "max": "#8B0000",  # Dark red
}

# TODO use a dynamic approach later on
dropdown_position_x = {
    "simulation": 0.02,
    "request": 0.15,
    "timestamp": 0.75,
}

# dark mode makes the active selection illegible
# https://github.com/plotly/plotly.js/issues/1428
updatemenus_default = {
    "direction": "down",
    "showactive": True,
    "x": 0.02,
    "xanchor": "left",
    "y": 1.08,
    "yanchor": "top",
    "bgcolor": "#d0d0d0",  # Light gray background for better hover contrast
    "bordercolor": "#555555",
    "borderwidth": 1,
    "font": {"size": 11, "color": "#000000"},
    "pad": {"r": 10, "t": 5, "b": 5, "l": 10},
}


def parse_simulation_csv(csv_path: Path) -> pd.DataFrame:
    """Parse simulation.csv and return successful requests.

    Example of a simulation.csv

    record_type,scenario_name,group_hierarchy,request_name,status,start_timestamp,end_timestamp,response_time_ms,error_message,event_type,duration_ms,cumulated_response_time_ms,is_incoming
    request,,,events,OK,1751199294083,1751199294256,173,,,,,false
    """
    try:
        df = pd.read_csv(csv_path)
    except Exception as e:
        print(f"Error reading CSV file {csv_path}: {e}", file=sys.stderr)
        sys.exit(1)

    # only consider response times of successful requests (ignore group and user entries in csv)
    request_df = df[(df["record_type"] == "request") & (df["status"] == "OK")].copy()

    if request_df.empty:
        print(f"No successful request records found in {csv_path}", file=sys.stderr)
        sys.exit(1)

    # Ensure data types are as expected
    request_df["start_timestamp"] = pd.to_datetime(request_df["start_timestamp"], unit="ms")
    request_df["end_timestamp"] = pd.to_datetime(request_df["end_timestamp"], unit="ms")
    request_df["response_time_ms"] = pd.to_numeric(request_df["response_time_ms"])

    return request_df


def calculate_percentiles(response_times: list[float], method: str = "exact") -> dict[str, float]:
    if method == "tdigest":
        return calculate_percentiles_tdigest(response_times)
    else:
        return calculate_percentiles_exact(response_times)


def calculate_percentiles_exact(response_times: list[float]) -> dict[str, float]:
    """Calculate exact percentiles using numpy."""
    if not response_times:
        return {"min": 0, "50th": 0, "75th": 0, "95th": 0, "99th": 0, "max": 0}

    # https://numpy.org/doc/stable/reference/generated/numpy.percentile.html#numpy-percentile
    percentiles = np.percentile(response_times, [0, 50, 75, 95, 99, 100], method="nearest")

    return {
        "min": percentiles[0],
        "50th": percentiles[1],
        "75th": percentiles[2],
        "95th": percentiles[3],
        "99th": percentiles[4],
        "max": percentiles[5],
    }


def calculate_percentiles_tdigest(response_times: list[float]) -> dict[str, float]:
    """Calculate percentiles using T-Digest algorithm (like Gatling which uses https://github.com/tdunning/t-digest)."""
    if not response_times:
        return {"min": 0, "50th": 0, "75th": 0, "95th": 0, "99th": 0, "max": 0}

    digest = TDigest()
    for time in response_times:
        digest.update(time)

    return {
        "min": digest.percentile(0),
        "50th": digest.percentile(50),
        "75th": digest.percentile(75),
        "95th": digest.percentile(95),
        "99th": digest.percentile(99),
        "max": digest.percentile(100),
    }


class SimulationResult(NamedTuple):
    """Container for simulation processing results."""

    directory: str
    simulation: str
    run_timestamp: datetime
    run_timestamp_display: str
    request_name: str
    count: int
    percentiles: dict[str, float]


def parse_gating_directory_name(dir_name: str) -> tuple[str, str] | None:
    """Parse directory name to extract simulation name and timestamp from Gatlings report directory
    naming convention of <simulation>-<timestamp>

    Returns: (simulation, timestamp) or None if format doesn't match
    """
    match = re.match(r"^(.+)-([0-9]+)$", dir_name)
    if match:
        return match.group(1), match.group(2)
    return None


def parse_gatling_directory_timestamp(timestamp_str: str) -> datetime:
    """Parse directory timestamp string to datetime object.

    Input: '20250627064559771' (YYYYMMDDHHMMSSmmm)
    Output: datetime object
    """
    try:
        year = timestamp_str[0:4]
        month = timestamp_str[4:6]
        day = timestamp_str[6:8]
        hour = timestamp_str[8:10]
        minute = timestamp_str[10:12]
        second = timestamp_str[12:14]
        milliseconds = timestamp_str[14:17] if len(timestamp_str) >= 17 else "000"

        dt = datetime(
            int(year),
            int(month),
            int(day),
            int(hour),
            int(minute),
            int(second),
            int(milliseconds) * 1000,
        )
        return dt
    except (ValueError, IndexError):
        return datetime.min


def format_timestamp(timestamp_str: str) -> str:
    """Convert timestamp string to human-readable format.

    Input: '20250627064559771' (YYYYMMDDHHMMSSmmm)
    Output: '2025-06-27 06:45:59'
    """
    dt = parse_gatling_directory_timestamp(timestamp_str)
    if dt == datetime.min:
        return timestamp_str
    return dt.strftime("%Y-%m-%d %H:%M:%S")


def truncate_string(string: str, max_length: int = 25) -> str:
    """Truncate string to max_length characters, adding ... if truncated."""
    if len(string) <= max_length:
        return string
    return string[: max_length - 3] + "..."


def is_multiple_reports_directory(directory: Path) -> bool:
    """Check if directory contains multiple simulation report subdirectories."""
    if not directory.is_dir():
        return False

    # if the directory itself contains simulation.csv = single report directory
    if (directory / "simulation.csv").exists():
        return False

    # Look for subdirectories with the pattern <simulation>_<timestamp>
    for subdir in directory.iterdir():
        if subdir.is_dir() and parse_gating_directory_name(subdir.name):
            if (subdir / "simulation.csv").exists():
                return True

    return False


def process_report_directory(
    report_dir: Path, simulation: str = None, run_timestamp: str = None, method: str = "exact"
) -> list[SimulationResult]:
    """Process single report directory and return results with optional info."""
    df = parse_simulation_csv(report_dir / "simulation.csv")

    # If no simulation/timestamp provided, try to parse from directory name
    if simulation is None or run_timestamp is None:
        parsed = parse_gating_directory_name(report_dir.name)
        if parsed:
            simulation, run_timestamp = parsed
        else:
            # Fallback for single directory mode
            simulation = simulation or "unknown"
            run_timestamp = run_timestamp or "unknown"

    results = []
    for request_name, group in df.groupby("request_name"):
        response_times = group["response_time_ms"].tolist()
        count = len(response_times)
        percentiles = calculate_percentiles(response_times, method)
        results.append(
            SimulationResult(
                report_dir.name,
                simulation,
                parse_gatling_directory_timestamp(run_timestamp),
                format_timestamp(run_timestamp),
                request_name,
                count,
                percentiles,
            )
        )

    return results


def process_multiple_reports(base_dir: Path, method: str = "exact") -> list[SimulationResult]:
    """Process directory containing multiple simulation report subdirectories."""
    all_results = []

    for subdir in sorted(base_dir.iterdir()):
        if not subdir.is_dir():
            continue

        parsed = parse_gating_directory_name(subdir.name)
        if not parsed:
            continue

        simulation, run_timestamp = parsed
        simulation_csv = subdir / "simulation.csv"

        if not simulation_csv.exists():
            print(f"Warning: simulation.csv not found in {subdir}, skipping", file=sys.stderr)
            continue

        try:
            results = process_report_directory(subdir, simulation, run_timestamp, method)
            all_results.extend(results)
        except Exception as e:
            print(f"Warning: Error processing {subdir}: {e}", file=sys.stderr)
            continue

    if not all_results:
        print(f"No valid simulation reports found in {base_dir}", file=sys.stderr)
        sys.exit(1)

    return all_results


def process_report_directory_for_plotting(
    report_dir: Path, simulation: str = None, run_timestamp: str = None
) -> dict[str, dict[str, dict[str, list[float]]]]:
    """Process report directory and return raw response times for plotting.

    Returns nested dict: {simulation: {run_timestamp: {request_name: [response_times]}}}
    """
    df = parse_simulation_csv(report_dir / "simulation.csv")

    # If no simulation/timestamp provided, try to parse from directory name
    if simulation is None or run_timestamp is None:
        parsed = parse_gating_directory_name(report_dir.name)
        if parsed:
            simulation, run_timestamp = parsed
        else:
            # Fallback for single directory mode
            simulation = simulation or "unknown"
            run_timestamp = run_timestamp or "unknown"

    # Group by request_name and return raw response times
    raw_data = {}
    for request_name, group in df.groupby("request_name"):
        raw_data[request_name] = group["response_time_ms"].tolist()

    return {simulation: {run_timestamp: raw_data}}


def process_report_directory_for_scatter_plotting(
    report_dir: Path, simulation: str = None, run_timestamp: str = None
) -> dict[str, dict[str, dict[str, list[tuple[int, int, float]]]]]:
    """Process report directory and return response times with timestamps for scatter plotting.

    Returns nested dict: {simulation: {run_timestamp:
                         {request_name: [(start_timestamp, end_timestamp, response_time)]}}}
    """
    simulation_csv = report_dir / "simulation.csv"
    df = parse_simulation_csv(simulation_csv)

    # If no simulation/timestamp provided, try to parse from directory name
    if simulation is None or run_timestamp is None:
        parsed = parse_gating_directory_name(report_dir.name)
        if parsed:
            simulation, run_timestamp = parsed
        else:
            # Fallback for single directory mode
            simulation = simulation or "unknown"
            run_timestamp = run_timestamp or "unknown"

    # Group by request_name and return timestamps with response times
    raw_data = {}
    for request_name, group in df.groupby("request_name"):
        # Combine start_timestamp, end_timestamp and response_time_ms into tuples
        timestamp_response_pairs = list(
            zip(
                group["start_timestamp"],
                group["end_timestamp"],
                group["response_time_ms"],
                strict=False,
            )
        )
        raw_data[request_name] = timestamp_response_pairs

    return {simulation: {run_timestamp: raw_data}}


def process_multiple_reports_for_plotting(
    base_dir: Path,
) -> dict[str, dict[str, dict[str, list[float]]]]:
    """Process directory containing multiple simulation reports for plotting.

    Returns nested dict: {simulation: {run_timestamp: {request_name: [response_times]}}}
    """
    all_data = {}

    for subdir in sorted(base_dir.iterdir()):
        if not subdir.is_dir():
            continue

        parsed = parse_gating_directory_name(subdir.name)
        if not parsed:
            continue

        simulation, run_timestamp = parsed
        simulation_csv = subdir / "simulation.csv"

        if not simulation_csv.exists():
            print(f"Warning: simulation.csv not found in {subdir}, skipping", file=sys.stderr)
            continue

        try:
            data = process_report_directory_for_plotting(subdir, simulation, run_timestamp)
            # Merge the nested dictionaries
            for sim, runs in data.items():
                if sim not in all_data:
                    all_data[sim] = {}
                all_data[sim].update(runs)
        except Exception as e:
            print(f"Warning: Error processing {subdir}: {e}", file=sys.stderr)
            continue

    return all_data


def process_multiple_reports_for_scatter_plotting(
    base_dir: Path,
) -> dict[str, dict[str, dict[str, list[tuple[int, int, float]]]]]:
    """Process directory containing multiple simulation reports for scatter plotting.

    Returns nested dict: {simulation: {run_timestamp:
                         {request_name: [(start_timestamp, end_timestamp, response_time)]}}}
    """
    all_data = {}

    for subdir in sorted(base_dir.iterdir()):
        if not subdir.is_dir():
            continue

        parsed = parse_gating_directory_name(subdir.name)
        if not parsed:
            continue

        simulation, run_timestamp = parsed
        simulation_csv = subdir / "simulation.csv"

        if not simulation_csv.exists():
            print(f"Warning: simulation.csv not found in {subdir}, skipping", file=sys.stderr)
            continue

        try:
            data = process_report_directory_for_scatter_plotting(subdir, simulation, run_timestamp)
            # Merge the nested dictionaries
            for sim, runs in data.items():
                if sim not in all_data:
                    all_data[sim] = {}
                all_data[sim].update(runs)
        except Exception as e:
            print(f"Warning: Error processing {subdir}: {e}", file=sys.stderr)
            continue

    return all_data


def plot_percentiles_stacked(results: list[SimulationResult]) -> go.Figure:
    """Plot stacked bar chart of percentiles across runs."""

    # convert results to DataFrame for easier processing
    data = []
    for result in results:
        row = {
            "directory": result.directory,
            "simulation": result.simulation,
            "run_timestamp": result.run_timestamp,
            "run_timestamp_formatted": result.run_timestamp_display,
            "request_name": result.request_name,
            "count": result.count,
            **result.percentiles,
        }
        data.append(row)

    if not data:
        return go.Figure()

    df = pd.DataFrame(data)

    # Get unique simulations and requests for dropdowns
    simulations = sorted(df["simulation"].unique())
    all_requests = sorted(df["request_name"].unique())

    # Default to first simulation and first request
    default_simulation = simulations[0] if simulations else None
    default_request = all_requests[0] if all_requests else None

    if not default_simulation or not default_request:
        return go.Figure()

    # Create traces for all combinations
    fig = go.Figure()

    # Create traces for each simulation-request combination
    trace_mapping = {}
    trace_idx = 0

    for simulation in simulations:
        sim_data = df[df["simulation"] == simulation]

        for request_name in sorted(sim_data["request_name"].unique()):
            request_data = sim_data[sim_data["request_name"] == request_name].copy()
            request_data = request_data.sort_values("run_timestamp")

            # Calculate stack heights (differences between percentiles)
            request_data["range_0_50"] = request_data["50th"] - request_data["min"]
            request_data["range_50_75"] = request_data["75th"] - request_data["50th"]
            request_data["range_75_95"] = request_data["95th"] - request_data["75th"]
            request_data["range_95_99"] = request_data["99th"] - request_data["95th"]
            request_data["range_99_max"] = request_data["max"] - request_data["99th"]

            # Determine visibility
            is_default = simulation == default_simulation and request_name == default_request

            start_trace_idx = trace_idx

            # Create stacked bars for each percentile range
            ranges = [
                ("0-50th", "range_0_50", request_data["min"]),
                ("50th-75th", "range_50_75", request_data["50th"]),
                ("75th-95th", "range_75_95", request_data["75th"]),
                ("95th-99th", "range_95_99", request_data["95th"]),
                ("99th-max", "range_99_max", request_data["99th"]),
            ]

            for range_name, height_col, base_col in ranges:
                fig.add_trace(
                    go.Bar(
                        x=request_data["run_timestamp_formatted"],
                        y=request_data[height_col],
                        base=base_col,
                        name=range_name,
                        marker_color=percentile_range_colors[range_name],
                        visible=is_default,
                        showlegend=is_default,
                        hovertemplate=(
                            f"<b>{range_name}</b><br>"
                            "Timestamp: %{x}<br>"
                            "Range: %{base:.0f}ms - %{customdata:.0f}ms<br>"
                            "<extra></extra>"
                        ),
                        customdata=base_col + request_data[height_col],
                    )
                )
                trace_idx += 1

            # Store mapping for dropdown functionality
            trace_mapping[(simulation, request_name)] = (start_trace_idx, trace_idx)

    # Create dropdown for simulation selection
    simulation_buttons = []
    for simulation in simulations:
        sim_data = df[df["simulation"] == simulation]
        sim_requests = sorted(sim_data["request_name"].unique())

        # Show first request of this simulation by default
        if sim_requests:
            first_request = sim_requests[0]
            visibility = [False] * len(fig.data)

            if (simulation, first_request) in trace_mapping:
                start_idx, end_idx = trace_mapping[(simulation, first_request)]
                for j in range(start_idx, end_idx):
                    if j < len(visibility):
                        visibility[j] = True

            simulation_buttons.append(
                {
                    "label": truncate_string(simulation),
                    "method": "update",
                    "args": [{"visible": visibility}, {"title": "Response Time Percentiles"}],
                }
            )

    # Create dropdown for request selection (initially for default simulation)
    request_buttons = []
    if default_simulation:
        sim_data = df[df["simulation"] == default_simulation]
        sim_requests = sorted(sim_data["request_name"].unique())

        for request_name in sim_requests:
            visibility = [False] * len(fig.data)

            if (default_simulation, request_name) in trace_mapping:
                start_idx, end_idx = trace_mapping[(default_simulation, request_name)]
                for j in range(start_idx, end_idx):
                    if j < len(visibility):
                        visibility[j] = True

            request_buttons.append(
                {
                    "label": truncate_string(request_name, 100),
                    "method": "update",
                    "args": [{"visible": visibility}, {"title": "Response Time Percentiles"}],
                }
            )

    fig.update_layout(
        xaxis_title="Run Timestamp",
        yaxis_title="Response Time (ms)",
        barmode="relative",  # this creates the stacking effect
        template="plotly_dark",
        font=dict(size=12),
        showlegend=True,
        legend=dict(
            orientation="v", yanchor="top", y=0.8, xanchor="left", x=1.02, title="Percentile Ranges"
        ),
        updatemenus=[
            updatemenus_default
            | {
                "buttons": simulation_buttons,
                "x": dropdown_position_x["simulation"],
            },
            updatemenus_default
            | {
                "buttons": request_buttons,
                "x": dropdown_position_x["request"],
            },
        ],
    )

    return fig


# TODO add mean to show how its not a good measure compared to the median or other percentiles
def plot_percentiles(
    results: list[SimulationResult], raw_data: dict[str, dict[str, dict[str, list[float]]]]
) -> go.Figure:
    """Plot histogram of response times highlighting percentile ranges."""
    fig = make_subplots(rows=1, cols=1)

    if not raw_data:
        return fig

    # Get all simulations, runs, and requests
    simulations = sorted(raw_data.keys())

    # Default to first simulation, first run, first request for initial display
    default_simulation = simulations[0] if simulations else None
    default_run = None
    default_request = None

    if default_simulation and raw_data[default_simulation]:
        runs = sorted(raw_data[default_simulation].keys())
        default_run = runs[0] if runs else None

        if default_run and raw_data[default_simulation][default_run]:
            requests = sorted(raw_data[default_simulation][default_run].keys())
            default_request = requests[0] if requests else None

    if not default_simulation or not default_run or not default_request:
        return fig

    # Create traces for all combinations (initially all hidden except default)
    trace_mapping = {}  # Maps (simulation, run, request) to trace indices
    trace_idx = 0

    for simulation in simulations:
        for run_timestamp in sorted(raw_data[simulation].keys()):
            for request_name in sorted(raw_data[simulation][run_timestamp].keys()):
                response_times = raw_data[simulation][run_timestamp][request_name]

                # Find corresponding percentiles
                percentiles = None
                for result in results:
                    if (
                        result.simulation == simulation
                        and result.run_timestamp == run_timestamp
                        and result.request_name == request_name
                    ):
                        percentiles = result.percentiles
                        break

                if not percentiles or not response_times:
                    continue

                # Determine if this should be initially visible
                is_default = (
                    simulation == default_simulation
                    and run_timestamp == default_run
                    and request_name == default_request
                )

                # Calculate histogram
                counts, bin_edges = np.histogram(response_times, bins=50)
                bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2
                percentages = (counts / len(response_times)) * 100

                # Create bar trace
                fig.add_trace(
                    go.Bar(
                        x=bin_centers,
                        y=percentages,
                        width=np.diff(bin_edges),
                        name=f"{simulation}_{run_timestamp}_{request_name}_histogram",
                        visible=is_default,
                        opacity=0.7,
                        marker_color="lightblue",
                        hovertemplate="<b>%{x:.0f}ms</b><br>"
                        + "OK: %{customdata}<br>"
                        + f"Total: {len(response_times)}<br>"
                        + "<extra></extra>",
                        customdata=counts,
                        showlegend=False,
                    )
                )

                start_trace_idx = trace_idx
                trace_idx += 1

                for percentile_name, color in percentile_line_colors.items():
                    if percentile_name in percentiles:
                        fig.add_trace(
                            go.Scatter(
                                x=[percentiles[percentile_name], percentiles[percentile_name]],
                                y=[0, max(percentages) if percentages.size > 0 else 100],
                                mode="lines",
                                line=dict(color=color, width=2, dash="dash"),
                                name=f"{percentile_name}: {percentiles[percentile_name]:.0f}ms",
                                visible=is_default,
                                hovertemplate=f"<b>{percentile_name} Percentile</b><br>"
                                + f"{percentiles[percentile_name]:.0f}ms<br>"
                                + "<extra></extra>",
                                showlegend=False,
                            )
                        )
                        trace_idx += 1

                # Store mapping
                trace_mapping[(simulation, run_timestamp, request_name)] = (
                    start_trace_idx,
                    trace_idx,
                )

    # Create dropdown for simulation selection
    simulation_buttons = []
    for simulation in simulations:
        # Show first run and first request of this simulation by default
        sim_runs = sorted(raw_data[simulation].keys())
        if sim_runs:
            first_run = sim_runs[0]
            sim_requests = sorted(raw_data[simulation][first_run].keys())
            if sim_requests:
                first_request = sim_requests[0]
                visibility = [False] * len(fig.data)

                if (simulation, first_run, first_request) in trace_mapping:
                    start_idx, end_idx = trace_mapping[(simulation, first_run, first_request)]
                    for j in range(start_idx, end_idx):
                        if j < len(visibility):
                            visibility[j] = True

                simulation_buttons.append(
                    {
                        "label": truncate_string(simulation),
                        "method": "update",
                        "args": [{"visible": visibility}, {"title": "Response Time Distribution"}],
                    }
                )

    # Create dropdown for request selection (initially for default simulation)
    request_buttons = []
    if default_simulation and default_run:
        sim_requests = sorted(raw_data[default_simulation][default_run].keys())

        for request_name in sim_requests:
            visibility = [False] * len(fig.data)

            if (default_simulation, default_run, request_name) in trace_mapping:
                start_idx, end_idx = trace_mapping[(default_simulation, default_run, request_name)]
                for j in range(start_idx, end_idx):
                    if j < len(visibility):
                        visibility[j] = True

            request_buttons.append(
                {
                    "label": truncate_string(request_name, 100),
                    "method": "update",
                    "args": [{"visible": visibility}, {"title": "Response Time Distribution"}],
                }
            )

    # Create dropdown for run timestamp selection (initially for default simulation)
    run_buttons = []
    if default_simulation:
        sim_runs = sorted(raw_data[default_simulation].keys())

        for run_timestamp in sim_runs:
            visibility = [False] * len(fig.data)

            if (default_simulation, run_timestamp, default_request) in trace_mapping:
                start_idx, end_idx = trace_mapping[
                    (default_simulation, run_timestamp, default_request)
                ]
                for j in range(start_idx, end_idx):
                    if j < len(visibility):
                        visibility[j] = True

            run_buttons.append(
                {
                    "label": run_timestamp,
                    "method": "update",
                    "args": [{"visible": visibility}, {"title": "Response Time Distribution"}],
                }
            )

    fig.update_layout(
        xaxis_title="Response Time (ms)",
        yaxis_title="Number of requests",
        template="plotly_dark",
        showlegend=False,
        font=dict(size=14),
        xaxis=dict(title=dict(font=dict(size=16))),
        yaxis=dict(title=dict(font=dict(size=16))),
        updatemenus=[
            updatemenus_default
            | {
                "buttons": simulation_buttons,
                "x": dropdown_position_x["simulation"],
            },
            updatemenus_default
            | {
                "buttons": request_buttons,
                "x": dropdown_position_x["request"],
            },
            updatemenus_default
            | {
                "buttons": run_buttons,
                "x": dropdown_position_x["timestamp"],
            },
        ],
    )

    return fig


def plot_scatter(
    scatter_data: dict[str, dict[str, dict[str, list[tuple[int, int, float]]]]],
) -> go.Figure:
    """Plot response times."""

    fig = go.Figure()

    if not scatter_data:
        return fig

    # Get all simulations, runs, and requests
    simulations = sorted(scatter_data.keys())

    # Default to first simulation, first run, first request for initial display
    default_simulation = simulations[0] if simulations else None
    default_run = None
    default_request = None

    if default_simulation and scatter_data[default_simulation]:
        runs = sorted(scatter_data[default_simulation].keys())
        default_run = runs[0] if runs else None

        if default_run and scatter_data[default_simulation][default_run]:
            requests = sorted(scatter_data[default_simulation][default_run].keys())
            default_request = requests[0] if requests else None

    if not default_simulation or not default_run or not default_request:
        return fig

    # Create traces for all combinations (initially all hidden except default)
    trace_mapping = {}  # Maps (simulation, run, request) to trace index
    trace_idx = 0

    for simulation in simulations:
        for run_timestamp in sorted(scatter_data[simulation].keys()):
            for request_name in sorted(scatter_data[simulation][run_timestamp].keys()):
                timestamp_response_pairs = scatter_data[simulation][run_timestamp][request_name]

                if not timestamp_response_pairs:
                    continue

                # Extract start timestamps, end timestamps and response times
                start_timestamps, end_timestamps, response_times = zip(
                    *timestamp_response_pairs, strict=False
                )

                # Determine if this should be initially visible
                is_default = (
                    simulation == default_simulation
                    and run_timestamp == default_run
                    and request_name == default_request
                )

                # Create scatter trace
                fig.add_trace(
                    go.Scatter(
                        x=end_timestamps,
                        y=response_times,
                        mode="markers",
                        name=f"{simulation}_{run_timestamp}_{request_name}",
                        visible=is_default,
                        marker=dict(size=6, opacity=0.7, color="lightblue"),
                        hovertemplate=(
                            "<b>%{y:.0f}ms</b><br>"
                            "End time: %{x}<br>"
                            f"Simulation: {truncate_string(simulation)}<br>"
                            f"Run: {format_timestamp(run_timestamp)}<br>"
                            f"Request: {truncate_string(request_name)}<br>"
                            "<extra></extra>"
                        ),
                        showlegend=False,
                    )
                )

                # Store mapping
                trace_mapping[(simulation, run_timestamp, request_name)] = trace_idx
                trace_idx += 1

    # Create comprehensive dropdown with all combinations
    all_combinations = []

    for simulation in simulations:
        for run_timestamp in sorted(scatter_data[simulation].keys()):
            for request_name in sorted(scatter_data[simulation][run_timestamp].keys()):
                if (simulation, run_timestamp, request_name) in trace_mapping:
                    visibility = [False] * len(fig.data)
                    trace_idx = trace_mapping[(simulation, run_timestamp, request_name)]
                    visibility[trace_idx] = True

                    # TODO create 3 dropdowns so it looks like in other plots?
                    # Create hierarchical label with formatted timestamp
                    formatted_simulation = truncate_string(simulation)
                    formatted_ts = format_timestamp(run_timestamp)
                    formated_request = truncate_string(request_name)
                    label = f"{formatted_simulation} | {formatted_ts} | {formated_request}"

                    all_combinations.append(
                        {
                            "label": label,
                            "method": "update",
                            "args": [
                                {"visible": visibility},
                            ],
                        }
                    )

    fig.update_layout(
        xaxis_title="Time",
        yaxis_title="Response Time (ms)",
        template="plotly_dark",
        showlegend=False,
        font=dict(size=14),
        xaxis=dict(
            title=dict(font=dict(size=16)),
            tickformat="%H:%M:%S",
            tickangle=45,
            showgrid=True,
            gridcolor="rgba(128, 128, 128, 0.3)",
            dtick=1000,  # 1 second intervals (1000ms)
        ),
        yaxis=dict(title=dict(font=dict(size=16))),
        updatemenus=[
            updatemenus_default
            | {
                "buttons": all_combinations,
            }
        ]
        if all_combinations
        else [],
    )

    return fig


def format_output(results: list[SimulationResult]) -> None:
    """Format and print results as CSV."""
    # Always use the full format with directory, simulation and run_timestamp columns
    print("directory,simulation,run_timestamp,request_name,count,min,50th,75th,95th,99th,max")

    # Sort results by directory, simulation, run_timestamp, request_name
    sorted_results = sorted(
        results, key=lambda r: (r.directory, r.simulation, r.run_timestamp, r.request_name)
    )

    for result in sorted_results:
        formatted_timestamp = result.run_timestamp_display

        print(
            f"{result.directory},{result.simulation},{formatted_timestamp},{result.request_name},{result.count},"
            f"{result.percentiles['min']:.0f},"
            f"{result.percentiles['50th']:.0f},"
            f"{result.percentiles['75th']:.0f},"
            f"{result.percentiles['95th']:.0f},"
            f"{result.percentiles['99th']:.0f},"
            f"{result.percentiles['max']:.0f}"
        )


def main():
    """CLI entry point - can be called as 'percentiles' command."""
    parser = argparse.ArgumentParser(
        description="Calculate percentiles from Gatling simulation.csv files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Single report directory
  gstat ./samples/trackerexportertests-20250627064559771

  # Multiple report directories
  gstat ./samples/

  # With distribution plotting (default)
  gstat ./samples/ --plot
  gstat ./samples/ --plot distribution

  # With stacked percentile bar chart
  gstat ./samples/ --plot stacked

  # With scatter plot of response times over time
  gstat ./samples/ --plot scatter
        """,
    )
    parser.add_argument(
        "report_directory",
        type=Path,
        help="Directory containing simulation.csv file, or directory with multiple reports",
    )
    parser.add_argument(
        "--plot",
        nargs="?",
        const="distribution",
        choices=["distribution", "stacked", "scatter"],
        help="Generate interactive plot instead of CSV output (default: distribution)",
    )
    parser.add_argument(
        "--output", "-o", type=Path, help="Output file for plot (default: show in browser)"
    )
    parser.add_argument(
        "--method",
        choices=["exact", "tdigest"],
        default="exact",
        help="Percentile calculation method (default: exact)",
    )
    argcomplete.autocomplete(parser)
    args = parser.parse_args()

    if not args.report_directory.exists():
        print(f"Directory does not exist: {args.report_directory}", file=sys.stderr)
        sys.exit(1)

    if not args.report_directory.is_dir():
        print(f"Path is not a directory: {args.report_directory}", file=sys.stderr)
        sys.exit(1)

    is_multiple = is_multiple_reports_directory(args.report_directory)

    if args.plot:
        # Get percentile results for plotting
        if is_multiple:
            results = process_multiple_reports(args.report_directory, args.method)
        else:
            results = process_report_directory(args.report_directory, method=args.method)

        if args.plot == "stacked":
            fig = plot_percentiles_stacked(results)
        elif args.plot == "scatter":
            # For scatter plot, we need timestamp data
            if is_multiple:
                scatter_data = process_multiple_reports_for_scatter_plotting(args.report_directory)
            else:
                # Convert single report data to nested format for plotting function
                if results:
                    sim = results[0].simulation
                    run = results[0].run_timestamp
                    scatter_single = process_report_directory_for_scatter_plotting(
                        args.report_directory, sim, run
                    )
                    scatter_data = scatter_single
                else:
                    scatter_data = {}
            fig = plot_scatter(scatter_data)
        else:
            # For original distribution plot, we need both percentiles and raw data
            if is_multiple:
                raw_data = process_multiple_reports_for_plotting(args.report_directory)
            else:
                raw_data = process_report_directory_for_plotting(args.report_directory)
            fig = plot_percentiles(results, raw_data)

        if args.output:
            fig.write_html(args.output)
            print(f"Plot saved to {args.output}")
        else:
            fig.show()
    else:
        if is_multiple:
            results = process_multiple_reports(args.report_directory, args.method)
            format_output(results)
        else:
            results = process_report_directory(args.report_directory, method=args.method)
            format_output(results)


if __name__ == "__main__":
    main()
