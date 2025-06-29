# Performance Test Reliability Experiment

Run a controlled experiment to compare the variability of running DHIS2 performances tests on
different GitHub runners (standard Ubuntu vs BuildJet).

## Method

Workflow .github/workflows/tracker-performance-tests.yml is run these variations
1. GitHubs own Ubuntu runner with Gatlings [shareConnections](https://docs.gatling.io/reference/script/http/protocol/#shareconnections) off
2. GitHubs own Ubuntu runner with Gatlings [shareConnections](https://docs.gatling.io/reference/script/http/protocol/#shareconnections) on
3. BuildJet custom runner with Gatlings [shareConnections](https://docs.gatling.io/reference/script/http/protocol/#shareconnections) off
4. BuildJet custom runner with Gatlings [shareConnections](https://docs.gatling.io/reference/script/http/protocol/#shareconnections) on

The workflows are run 24 times a day and upload the Gatling report to GitHubs artifacts.

### Analysis

1. Download all artifacts `./workflows-download.sh`
2. Flatten the artifacts `./experiment-pre-process.sh`
3. Extract data out of Gatlings binary `simulation.log` into `simulation.csv`
3. TODO MAD analysis (maybe another step) to compare the variability within an environment

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

