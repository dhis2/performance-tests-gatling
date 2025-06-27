#!/usr/bin/env python3
"""
Gatling Percentiles Calculator - Dash Web App

Web application for calculating percentiles from Gatling simulation.csv files using T-Digest algorithm
to match Gatling's HTML report percentile calculations exactly.
"""

from pathlib import Path

import dash
import dash_bootstrap_components as dbc
import pandas as pd
from dash import Input, Output, State, callback, dash_table, dcc, html

from percentiles import (
    SimulationResult,
    create_interactive_plot,
    is_multiple_reports_directory,
    process_multiple_reports,
    process_multiple_reports_for_plotting,
    process_report_directory,
    process_report_directory_for_plotting,
)

# Initialize Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = "Gatling Percentiles Calculator"

# App layout
app.layout = dbc.Container(
    [
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.H1("Gatling Percentiles Calculator", className="text-center mb-4"),
                        html.P(
                            "Upload Gatling simulation.csv files or directories to calculate percentiles using T-Digest algorithm",
                            className="text-center text-muted mb-4",
                        ),
                    ]
                )
            ]
        ),
        dbc.Row(
            [
                dbc.Col(
                    [
                        dbc.Card(
                            [
                                dbc.CardBody(
                                    [
                                        html.H4("Load Data", className="card-title"),
                                        html.P(
                                            "Enter the path to a directory containing simulation.csv file(s):",
                                            className="text-muted",
                                        ),
                                        dbc.InputGroup(
                                            [
                                                dbc.Input(
                                                    id="directory-path-input",
                                                    placeholder="Enter directory path (e.g., ../samples/ or ./report-20250627/)",
                                                    type="text",
                                                    value="",
                                                ),
                                                dbc.Button(
                                                    "Load Data",
                                                    id="load-button",
                                                    color="primary",
                                                    n_clicks=0,
                                                ),
                                            ],
                                            className="mb-3",
                                        ),
                                        html.Div(id="load-status", className="mt-3"),
                                    ]
                                )
                            ],
                            className="mb-4",
                        )
                    ]
                )
            ]
        ),
        dbc.Row(
            [
                dbc.Col(
                    [
                        dbc.Card(
                            [
                                dbc.CardBody(
                                    [
                                        html.H4("Results", className="card-title"),
                                        dbc.Tabs(
                                            [
                                                dbc.Tab(label="Table View", tab_id="table-tab"),
                                                dbc.Tab(label="Plot View", tab_id="plot-tab"),
                                            ],
                                            id="tabs",
                                            active_tab="table-tab",
                                        ),
                                        html.Div(id="tab-content", className="mt-3"),
                                    ]
                                )
                            ]
                        )
                    ]
                )
            ]
        ),
        # Hidden div to store processed data
        dcc.Store(id="processed-data"),
        dcc.Store(id="raw-data-store"),
    ],
    fluid=True,
)


def process_directory_path(directory_path):
    """Process directory path and extract simulation data."""
    if not directory_path:
        return None, None, "Please enter a directory path."

    path = Path(directory_path)

    if not path.exists():
        return None, None, f"Directory does not exist: {directory_path}"

    if not path.is_dir():
        return None, None, f"Path is not a directory: {directory_path}"

    try:
        # Determine if this is a single report directory or multiple reports directory
        is_multiple = is_multiple_reports_directory(path)

        if is_multiple:
            results = process_multiple_reports(path)
            raw_data = process_multiple_reports_for_plotting(path)
        else:
            results = process_report_directory(path)
            # Convert single report data to nested format for plotting function
            if results:
                sim = results[0].simulation
                run = results[0].run_timestamp
                raw_single = process_report_directory_for_plotting(path, sim, run)
                raw_data = raw_single
            else:
                raw_data = {}

        if not results:
            return None, None, "No valid simulation data found in the specified directory."

        return (
            results,
            raw_data,
            f"Successfully processed {len(results)} request records from {'multiple reports' if is_multiple else 'single report'}.",
        )

    except Exception as e:
        return None, None, f"Error processing directory: {str(e)}"


@callback(
    [
        Output("processed-data", "data"),
        Output("raw-data-store", "data"),
        Output("load-status", "children"),
    ],
    [Input("load-button", "n_clicks")],
    [State("directory-path-input", "value")],
)
def process_directory(n_clicks, directory_path):
    """Process directory path and return processed data."""
    if n_clicks == 0:
        return None, None, ""

    results, raw_data, status_message = process_directory_path(directory_path)

    if not results:
        # Error or warning case
        if "does not exist" in status_message or "not a directory" in status_message:
            alert_color = "danger"
        else:
            alert_color = "warning"
        return None, None, dbc.Alert(status_message, color=alert_color)

    # Convert results to dict format for JSON serialization
    results_dict = []
    for result in results:
        results_dict.append(
            {
                "simulation": result.simulation,
                "run_timestamp": result.run_timestamp,
                "request_name": result.request_name,
                "count": result.count,
                "percentiles": result.percentiles,
            }
        )

    status_msg = dbc.Alert(status_message, color="success")
    return results_dict, raw_data, status_msg


@callback(
    Output("tab-content", "children"),
    [Input("tabs", "active_tab"), Input("processed-data", "data"), Input("raw-data-store", "data")],
)
def update_tab_content(active_tab, processed_data, raw_data_dict):
    """Update tab content based on selected tab and processed data."""
    if not processed_data:
        return html.Div("No data to display. Please upload files first.", className="text-muted")

    if active_tab == "table-tab":
        # Create DataFrame from processed data
        df_data = []
        for result in processed_data:
            row = {
                "simulation": result["simulation"],
                "run_timestamp": result["run_timestamp"],
                "request_name": result["request_name"],
                "count": result["count"],
                **{k: round(v, 0) for k, v in result["percentiles"].items()},
            }
            df_data.append(row)

        df = pd.DataFrame(df_data)

        # Create data table
        return dash_table.DataTable(
            data=df.to_dict("records"),
            columns=[
                {"name": "Simulation", "id": "simulation"},
                {"name": "Run Timestamp", "id": "run_timestamp"},
                {"name": "Request Name", "id": "request_name"},
                {"name": "Count", "id": "count", "type": "numeric"},
                {"name": "Min (ms)", "id": "min", "type": "numeric"},
                {"name": "50th (ms)", "id": "50th", "type": "numeric"},
                {"name": "75th (ms)", "id": "75th", "type": "numeric"},
                {"name": "95th (ms)", "id": "95th", "type": "numeric"},
                {"name": "99th (ms)", "id": "99th", "type": "numeric"},
                {"name": "Max (ms)", "id": "max", "type": "numeric"},
            ],
            style_table={"overflowX": "auto"},
            style_cell={"textAlign": "left", "padding": "10px"},
            style_header={"backgroundColor": "rgb(230, 230, 230)", "fontWeight": "bold"},
            style_data_conditional=[
                {"if": {"row_index": "odd"}, "backgroundColor": "rgb(248, 248, 248)"}
            ],
            sort_action="native",
            filter_action="native",
            page_action="native",
            page_current=0,
            page_size=20,
        )

    elif active_tab == "plot-tab":
        if not raw_data_dict:
            return html.Div("No plotting data available.", className="text-muted")

        # Convert dict back to SimulationResult objects for plotting
        results = []
        for result_dict in processed_data:
            results.append(
                SimulationResult(
                    result_dict["simulation"],
                    result_dict["run_timestamp"],
                    result_dict["request_name"],
                    result_dict["count"],
                    result_dict["percentiles"],
                )
            )

        # Create interactive plot
        fig = create_interactive_plot(results, raw_data_dict)

        return dcc.Graph(figure=fig, style={"height": "600px"})

    return html.Div("No content available for this tab.", className="text-muted")


def run_dash_app(host="127.0.0.1", port=8050, debug=True):
    """Run the Dash application."""
    app.run(host=host, port=port, debug=debug)


if __name__ == "__main__":
    run_dash_app()
