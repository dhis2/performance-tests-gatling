# Performance Test Reliability Experiment

## Method

TODO explain

## GHA

### Run workflows manually

```sh
gh workflow run "Tracker Performance - Ubuntu Default"
gh workflow run "Tracker Performance - Ubuntu Shared"
gh workflow run "Tracker Performance - BuildJet Default"
gh workflow run "Tracker Performance - BuildJet Shared"
```

### Delete all workflow runs and artifacts

To start fresh you can delete all runs for the 4 matrix workflows

```sh
gh run list --workflow="Tracker Performance - Ubuntu Default" --json databaseId --jq '.[].databaseId' | xargs -I {} gh run delete {}
gh run list --workflow="Tracker Performance - Ubuntu Shared" --json databaseId --jq '.[].databaseId' | xargs -I {} gh run delete {}
gh run list --workflow="Tracker Performance - BuildJet Default" --json databaseId --jq '.[].databaseId' | xargs -I {} gh run delete {}
gh run list --workflow="Tracker Performance - BuildJet Shared" --json databaseId --jq '.[].databaseId' | xargs -I {} gh run delete {}
```

This will automatically delete all the artifacts associated with those runs.

### Download all artifacts

Download all artifacts from the 4 matrix workflows into `./experiment` folder as zip files

```sh
./download-experiments.sh
```

### Pre-process for analysis

Organize artifacts into analysis structure with subfolders per experiment coordinate

```sh
./experiment-pre-process.sh
```

Creates structure: `analysis/{experiment-coordinate}/trackerexportertests-{timestamp}/`
