# Performance Test Reliability Experiment Analysis

Interactive analysis of DHIS2 performance test variability across different GitHub runners.

## Data

The experiment compares 4 configurations:
* `buildjet-2vcpu-ubuntu-2204` - BuildJet runner, shareConnections off
* `buildjet-2vcpu-ubuntu-2204-shared` - BuildJet runner, shareConnections on
* `ubuntu-24.04` - GitHub Ubuntu runner, shareConnections off
* `ubuntu-24.04-shared` - GitHub Ubuntu runner, shareConnections on

## Usage

Start the interactive analysis:

```bash
cd experiment-analysis
uv run jupyter lab
```

Open `analysis.ipynb` to explore the data with interactive box plots and robust statistics.

## Features

* **Box plots** showing response time distributions by experiment group
* **Robust statistics** (median, IQR, MAD) - no normal distribution assumptions
* **Time series analysis** of performance over time
* **Interactive filtering** and exploration tools
* **CSV export** of summary statistics
