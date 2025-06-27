# Gatling Percentiles Calculator

A Python CLI tool that calculates percentiles (min, 50th, 75th, 95th, 99th, max) from Gatling
`simulation.csv` files using the T-Digest algorithm to exactly match Gatling's HTML report
percentile calculations.

## Features

* **T-Digest Algorithm**: Uses the same T-Digest algorithm as Gatling for exact compatibility
* **Multiple Reports Support**: Process single reports or directories containing multiple simulation runs
* **Easy Installation**: Install globally like a binary using `uv`
* **CSV Output**: Outputs percentile data as CSV to console
* **Interactive Plotting**: Generate interactive HTML plots with simulation and request filtering

## Installation

### Global Installation (Recommended)

Install globally using `uv` for easy access from anywhere:

```bash
uv tool install .
```

Use the `percentiles` command from anywhere.

### Local Development

For development or one-time use:

```bash
uv sync
uv run percentiles <report_directory>
```

## Usage

### Basic Usage

```bash
# Single report directory
percentiles <report_directory>

# Multiple reports directory
percentiles <directory_containing_multiple_reports>

# Examples
percentiles ../samples/trackerexportertests-20250627064559771  # Single report
percentiles ../samples/                                        # Multiple reports
```

### Plotting

Generate interactive HTML plots instead of CSV output:

```bash
# Generate plot and open in browser
percentiles ../samples/ --plot

# Save plot to file
percentiles ../samples/ --plot --output my_plot.html
```

### Output Formats

#### Single Report Directory

For a single report directory, outputs CSV with these columns:
* `request_name`: HTTP request name/endpoint
* `count`: Number of successful requests
* `min`: Minimum response time (ms)
* `50th`: 50th percentile response time (ms)
* `75th`: 75th percentile response time (ms)
* `95th`: 95th percentile response time (ms)
* `99th`: 99th percentile response time (ms)
* `max`: Maximum response time (ms)

```csv
request_name,count,min,50th,75th,95th,99th,max
events,38,320,357,380,557,1258,1258
```

#### Multiple Reports Directory

For multiple reports, adds simulation and run timestamp columns:
* `simulation`: Name of the simulation extracted from directory name
* `run_timestamp`: Timestamp of the run extracted from directory name
* `request_name`: HTTP request name/endpoint
* `count`: Number of successful requests
* `min`: Minimum response time (ms)
* `50th`: 50th percentile response time (ms)
* `75th`: 75th percentile response time (ms)
* `95th`: 95th percentile response time (ms)
* `99th`: 99th percentile response time (ms)
* `max`: Maximum response time (ms)

```csv
simulation,run_timestamp,request_name,count,min,50th,75th,95th,99th,max
trackerexportertests,20250627064559771,events,38,320,357,380,557,1258,1258
trackerexportertests,20250627095400668,events,7,2138,2346,2383,3345,3345,3345
```

### Directory Structure

The tool automatically detects whether you're providing a single report or multiple reports:

* **Single Report**: Directory containing `simulation.csv` directly
* **Multiple Reports**: Directory containing subdirectories named `<simulation>-<timestamp>`, each with their own `simulation.csv`

Example multiple reports structure:
```
samples/
├── trackerexportertests-20250627064559771/
│   ├── simulation.csv
│   └── ...
└── trackerexportertests-20250627095400668/
    ├── simulation.csv
    └── ...
```

## How It Works

### Single Report Processing
1. **Reads** `simulation.csv` from the specified Gatling report directory
2. **Filters** for successful request records (`record_type=request` and `status=OK`)
3. **Groups** requests by `request_name` to handle multiple endpoints
4. **Calculates** percentiles using T-Digest algorithm with the same parameters as Gatling
5. **Outputs** results as CSV to stdout

### Multiple Reports Processing
1. **Detects** directory structure and identifies simulation report subdirectories
2. **Parses** directory names to extract simulation name and run timestamp (`<simulation>-<timestamp>`)
3. **Processes** each subdirectory's `simulation.csv` file individually
4. **Combines** results from all reports with simulation and timestamp metadata
5. **Outputs** aggregated results as CSV with additional columns

## Troubleshooting

### Command Not Found

If `percentiles` command is not found after installation:

```bash
# Ensure uv's tool directory is in your PATH
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

### No Request Records Found

If you see "No successful request records found", check:

* The CSV file contains `record_type=request` records
* Some requests have `status=OK` (not all failed)
* The CSV format matches Gatling's output

### No Valid Simulation Reports Found

If you see "No valid simulation reports found", check:

* Directory contains subdirectories with the naming pattern `<simulation>-<timestamp>`
* Each subdirectory contains a `simulation.csv` file
* Directory names use hyphens (not underscores) to separate simulation from timestamp
* Timestamps are numeric (e.g., `20250627064559771`)

### Example Valid Directory Structure

```
samples/
├── trackerexportertests-20250627064559771/    # ✓ Valid: <name>-<timestamp>
│   └── simulation.csv
├── trackerexportertests-20250627095400668/    # ✓ Valid: <name>-<timestamp>
│   └── simulation.csv
├── invalid_name_format/                        # ✗ Invalid: uses underscores
└── missing-csv-20250627064559771/              # ✗ Invalid: no simulation.csv
```

## Prerequisites

* **Python**: Python 3.13 or higher (managed automatically by uv)
* **uv**: Python package and project manager https://docs.astral.sh/uv

## Development

### Setup

```bash
cd stats/

# Install Python 3.13 and create virtual environment
uv sync

# Install pre-commit hooks for code formatting
uv run pre-commit install
```

### Development Commands

```bash
# Run the tool locally
uv run percentiles <report_directory>

# Format code with ruff
uv run ruff format .

# Check and fix linting issues
uv run ruff check . --fix

# Run pre-commit hooks manually
uv run pre-commit run --all-files

# Install as global tool for testing
uv tool install .
```

### Pre-commit Hooks

This project uses pre-commit hooks to ensure code quality. The hooks automatically:

* Format code using `ruff format`
* Fix linting issues using `ruff check --fix`

These hooks run automatically on `git commit`. To bypass temporarily: `git commit --no-verify`

