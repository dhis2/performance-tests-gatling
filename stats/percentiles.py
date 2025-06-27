#!/usr/bin/env python3
"""
Gatling Percentiles Calculator

Calculate percentiles from Gatling simulation.csv files using T-Digest algorithm
to match Gatling's HTML report percentile calculations exactly.
"""

import argparse
import re
import sys
from pathlib import Path
from typing import NamedTuple

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from tdigest import TDigest


def parse_simulation_csv(csv_path: Path) -> pd.DataFrame:
    """Parse simulation.csv and return filtered request data."""
    try:
        df = pd.read_csv(csv_path)
    except Exception as e:
        print(f"Error reading CSV file {csv_path}: {e}", file=sys.stderr)
        sys.exit(1)

    # Filter for request records with OK status
    request_df = df[(df["record_type"] == "request") & (df["status"] == "OK")].copy()

    if request_df.empty:
        print(f"No successful request records found in {csv_path}", file=sys.stderr)
        sys.exit(1)

    # Ensure response_time_ms is numeric
    request_df["response_time_ms"] = pd.to_numeric(request_df["response_time_ms"], errors="coerce")
    request_df = request_df.dropna(subset=["response_time_ms"])

    return request_df


def calculate_percentiles_with_tdigest(response_times: list[float]) -> dict[str, float]:
    """Calculate percentiles using T-Digest algorithm (like Gatling)."""
    if not response_times:
        return {"min": 0, "50th": 0, "75th": 0, "95th": 0, "99th": 0, "max": 0}

    if len(response_times) == 1:
        val = response_times[0]
        return {"min": val, "50th": val, "75th": val, "95th": val, "99th": val, "max": val}

    # Create T-Digest with default parameters (matches Gatling behavior)
    digest = TDigest()
    for time in response_times:
        digest.update(time)

    return {
        "min": min(response_times),
        "50th": digest.percentile(50),
        "75th": digest.percentile(75),
        "95th": digest.percentile(95),
        "99th": digest.percentile(99),
        "max": max(response_times),
    }


class SimulationResult(NamedTuple):
    """Container for simulation processing results."""

    simulation: str
    run_timestamp: str
    request_name: str
    count: int
    percentiles: dict[str, float]


def parse_directory_name(dir_name: str) -> tuple[str, str] | None:
    """Parse directory name to extract simulation name and timestamp.

    Expected format: <simulation>-<timestamp>
    Returns: (simulation, timestamp) or None if format doesn't match
    """
    match = re.match(r"^(.+)-([0-9]+)$", dir_name)
    if match:
        return match.group(1), match.group(2)
    return None


def is_multiple_reports_directory(directory: Path) -> bool:
    """Check if directory contains multiple simulation report subdirectories."""
    if not directory.is_dir():
        return False

    # Check if the directory itself contains simulation.csv (single report directory)
    if (directory / "simulation.csv").exists():
        return False

    # Look for subdirectories with the pattern <simulation>_<timestamp>
    found_valid_subdirs = 0
    for subdir in directory.iterdir():
        if subdir.is_dir() and parse_directory_name(subdir.name):
            # Check if it contains simulation.csv
            if (subdir / "simulation.csv").exists():
                found_valid_subdirs += 1

    # Need at least one valid subdirectory to be considered multiple reports directory
    return found_valid_subdirs > 0


def process_report_directory(
    report_dir: Path, simulation: str = None, run_timestamp: str = None
) -> list[SimulationResult]:
    """Process single report directory and return results with optional info."""
    simulation_csv = report_dir / "simulation.csv"

    if not simulation_csv.exists():
        print(f"simulation.csv not found in {report_dir}", file=sys.stderr)
        sys.exit(1)

    df = parse_simulation_csv(simulation_csv)

    # If no simulation/timestamp provided, try to parse from directory name
    if simulation is None or run_timestamp is None:
        parsed = parse_directory_name(report_dir.name)
        if parsed:
            simulation, run_timestamp = parsed
        else:
            # Fallback for single directory mode
            simulation = simulation or "unknown"
            run_timestamp = run_timestamp or "unknown"

    # Group by request_name
    results = []
    for request_name, group in df.groupby("request_name"):
        response_times = group["response_time_ms"].tolist()
        count = len(response_times)
        percentiles = calculate_percentiles_with_tdigest(response_times)
        results.append(
            SimulationResult(simulation, run_timestamp, request_name, count, percentiles)
        )

    return results


def process_multiple_reports(base_dir: Path) -> list[SimulationResult]:
    """Process directory containing multiple simulation report subdirectories."""
    all_results = []

    for subdir in sorted(base_dir.iterdir()):
        if not subdir.is_dir():
            continue

        parsed = parse_directory_name(subdir.name)
        if not parsed:
            continue

        simulation, run_timestamp = parsed
        simulation_csv = subdir / "simulation.csv"

        if not simulation_csv.exists():
            print(f"Warning: simulation.csv not found in {subdir}, skipping", file=sys.stderr)
            continue

        try:
            results = process_report_directory(subdir, simulation, run_timestamp)
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
    simulation_csv = report_dir / "simulation.csv"

    if not simulation_csv.exists():
        print(f"simulation.csv not found in {report_dir}", file=sys.stderr)
        sys.exit(1)

    df = parse_simulation_csv(simulation_csv)

    # If no simulation/timestamp provided, try to parse from directory name
    if simulation is None or run_timestamp is None:
        parsed = parse_directory_name(report_dir.name)
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

        parsed = parse_directory_name(subdir.name)
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


def create_interactive_plot(
    results: list[SimulationResult], raw_data: dict[str, dict[str, dict[str, list[float]]]]
) -> go.Figure:
    """Create interactive Plotly figure showing response time distribution with percentiles."""

    # Create subplots
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

                # Add percentile lines
                percentile_colors = {
                    "50th": "green",
                    "75th": "orange",
                    "95th": "red",
                    "99th": "darkred",
                }

                for percentile_name, color in percentile_colors.items():
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

    # Create comprehensive dropdown with all combinations
    all_combinations = []

    for simulation in simulations:
        for run_timestamp in sorted(raw_data[simulation].keys()):
            for request_name in sorted(raw_data[simulation][run_timestamp].keys()):
                if (simulation, run_timestamp, request_name) in trace_mapping:
                    visibility = [False] * len(fig.data)
                    start_idx, end_idx = trace_mapping[(simulation, run_timestamp, request_name)]
                    for j in range(start_idx, end_idx):
                        if j < len(visibility):
                            visibility[j] = True

                    # Create hierarchical label
                    label = f"{simulation} | {run_timestamp} | {request_name}"

                    all_combinations.append(
                        {
                            "label": label,
                            "method": "update",
                            "args": [
                                {"visible": visibility},
                                {
                                    "title": dict(
                                        text=(
                                            "Response Time Distribution "
                                            "(simulation|timestamp|request)"
                                        ),
                                        x=0.5,
                                        xanchor="center",
                                        y=0.95,
                                        yanchor="top",
                                        font=dict(size=18, color="white"),
                                    )
                                },
                            ],
                        }
                    )

    # Update layout with single comprehensive dropdown
    fig.update_layout(
        title=dict(
            text="Response Time Distribution (simulation|timestamp|request)",
            x=0.5,
            xanchor="center",
            y=0.95,
            yanchor="top",
            font=dict(size=18, color="white"),
        ),
        xaxis_title="Response Time (ms)",
        yaxis_title="Percentage of Requests (%)",
        template="plotly_dark",
        showlegend=False,
        font=dict(size=14),
        xaxis=dict(title=dict(font=dict(size=16))),
        yaxis=dict(title=dict(font=dict(size=16))),
        updatemenus=[
            {
                "buttons": all_combinations,
                "direction": "down",
                "showactive": True,
                "x": 0.5,
                "xanchor": "center",
                "y": 1.05,
                "yanchor": "top",
                "bgcolor": "#2d2d2d",
                "bordercolor": "#555555",
                "borderwidth": 1,
                "font": {"size": 11, "color": "#ffffff"},
                "active": 0,
                "pad": {"r": 10, "t": 5, "b": 5, "l": 10},
            }
        ]
        if all_combinations
        else [],
        # Add some top margin for the dropdown
        margin=dict(t=120, b=60, l=60, r=60),
    )

    return fig


def format_output(results: list[SimulationResult], is_multiple: bool = False) -> None:
    """Format and print results as CSV."""
    # Always use the full format with simulation and run_timestamp columns
    print("simulation,run_timestamp,request_name,count,min,50th,75th,95th,99th,max")

    # Sort results by simulation, run_timestamp, request_name
    sorted_results = sorted(results, key=lambda r: (r.simulation, r.run_timestamp, r.request_name))

    # Print results
    for result in sorted_results:
        print(
            f"{result.simulation},{result.run_timestamp},{result.request_name},{result.count},"
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
        description="Calculate percentiles from Gatling simulation.csv using T-Digest algorithm",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Single report directory
  percentiles ./samples/trackerexportertests-20250627064559771

  # Multiple report directories
  percentiles ./samples/

  # With plotting
  percentiles ./samples/ --plot
        """,
    )
    parser.add_argument(
        "report_directory",
        type=Path,
        help="Directory containing simulation.csv file, or directory with multiple reports",
    )
    parser.add_argument(
        "--plot", action="store_true", help="Generate interactive plot instead of CSV output"
    )
    parser.add_argument(
        "--output", "-o", type=Path, help="Output file for plot (default: show in browser)"
    )

    args = parser.parse_args()

    if not args.report_directory.exists():
        print(f"Directory does not exist: {args.report_directory}", file=sys.stderr)
        sys.exit(1)

    if not args.report_directory.is_dir():
        print(f"Path is not a directory: {args.report_directory}", file=sys.stderr)
        sys.exit(1)

    # Determine if this is a single report directory or multiple reports directory
    is_multiple = is_multiple_reports_directory(args.report_directory)

    if args.plot:
        # For plotting, we need both percentiles and raw data
        if is_multiple:
            results = process_multiple_reports(args.report_directory)
            raw_data = process_multiple_reports_for_plotting(args.report_directory)
        else:
            results = process_report_directory(args.report_directory)
            # Convert single report data to nested format for plotting function
            if results:
                sim = results[0].simulation
                run = results[0].run_timestamp
                raw_single = process_report_directory_for_plotting(args.report_directory, sim, run)
                raw_data = raw_single
            else:
                raw_data = {}

        fig = create_interactive_plot(results, raw_data)

        if args.output:
            fig.write_html(args.output)
            print(f"Plot saved to {args.output}")
        else:
            fig.show()
    else:
        if is_multiple:
            results = process_multiple_reports(args.report_directory)
            format_output(results)
        else:
            results = process_report_directory(args.report_directory)
            format_output(results)


def run_dash_app(host="127.0.0.1", port=8050, debug=True):
    """Run the Dash web application."""
    try:
        import dash_app

        dash_app.run_dash_app(host=host, port=port, debug=debug)
    except ImportError as e:
        print(f"Error: Could not import dash_app module: {e}", file=sys.stderr)
        print("Make sure dash dependencies are installed with: uv sync", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
