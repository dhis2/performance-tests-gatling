#!/bin/bash
# Download all artifacts from the 6 matrix workflows

mkdir -p experiment-workflows-gh

# Function to download artifacts for a workflow, skipping already downloaded runs
download_workflow_artifacts() {
    local workflow_name="$1"
    local workflow_short_name="$2"

    echo "Downloading $workflow_short_name artifacts..."

    # Get all run IDs for the workflow
    gh run list --workflow="$workflow_name" --json databaseId --jq '.[].databaseId' | while read -r run_id; do
        # Check if we already have artifacts from this run
        if ls experiment-workflows-gh | grep -q "$run_id"; then
            continue
        else
            gh run download "$run_id" --dir experiment-workflows-gh 2>/dev/null || true
        fi
    done
}

# Download artifacts from each workflow
download_workflow_artifacts "Tracker Performance - Ubuntu Default" "Ubuntu Default"
download_workflow_artifacts "Tracker Performance - Ubuntu Shared" "Ubuntu Shared"
download_workflow_artifacts "Tracker Performance - BuildJet Default" "BuildJet Default"
download_workflow_artifacts "Tracker Performance - BuildJet Shared" "BuildJet Shared"
download_workflow_artifacts "Tracker Performance - Ubuntu Play" "Ubuntu Play"
download_workflow_artifacts "Tracker Performance - Ubuntu Play Shared" "Ubuntu Play Shared"

echo "Download complete! Check ./experiment-workflows-gh folder"
