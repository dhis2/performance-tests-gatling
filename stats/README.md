# gstat - Gatling Statistics Calculator

A Python CLI tool that calculates percentiles (min, 50th, 75th, 95th, 99th, max) from Gatling
`simulation.csv` files. Supports both exact percentile calculation (default) and T-Digest algorithm
approximation (matches Gatling's HTML report calculations).

## Features

* **Exact Percentiles**: Default method using NumPy for accurate percentile calculations
* **T-Digest Algorithm**: Optional method using the same T-Digest algorithm as Gatling for compatibility
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

Use the `gstat` command from anywhere.

### Local Development

For development or one-time use:

```bash
uv sync
uv run gstat <report_directory>
```

## Usage

Output percentiles per simulation, run and request name as CSV

```bash
gstat <report_directory>
```

* You must point to a report directory created by Gatling. Either a single report directory or a
directory containing multiple report directories.
* You must convert the binary `simulation.log` into a `simulation.csv`.

### CSV Output Format

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

### Percentile Calculation Methods

Choose between exact calculation (default) or T-Digest approximation:

```bash
# Use exact percentile calculation (default)
gstat <report_directory>

# Use T-Digest algorithm (matches Gatling's method)
gstat <report_directory> --method tdigest
```

### Plotting

Generate interactive HTML plots instead of CSV output:

```bash
# Generate plot and open in browser
gstat ../samples/ --plot

# Save plot to file
gstat ../samples/ --plot --output my_plot.html

# Combine with method selection
gstat ../samples/ --plot --method tdigest
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
uv run gstat <report_directory>

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

