#!/bin/bash
# Pre-process experiment data by organizing artifacts into analysis structure

EXPERIMENT_DIR="experiment-workflows-gh"
ANALYSIS_DIR="experiment-workflows-flat"
GATLING_PATTERN="trackerexportertests-*"
ARTIFACT_PREFIX="gatling-report-"

rm -rf "$ANALYSIS_DIR"
mkdir -p "$ANALYSIS_DIR"

echo "Pre-process artifacts in: $EXPERIMENT_DIR..."
if [[ ! -d "$EXPERIMENT_DIR" ]]; then
    echo "Error: $EXPERIMENT_DIR directory not found!"
    exit 1
fi

# Process all artifact folders in experiment folder
for artifact_dir in "$EXPERIMENT_DIR/$ARTIFACT_PREFIX"*; do
    if [[ -d "$artifact_dir" ]]; then
        # Extract experiment coordinate from folder name
        base_name=$(basename "$artifact_dir")

        # Remove 'gatling-report-' prefix and the last two dash-separated parts (run_id and sha)
        experiment_coord=$(echo "$base_name" | sed "s/^$ARTIFACT_PREFIX//" | sed 's/-[^-]*-[^-]*$//')

        target_dir="$ANALYSIS_DIR/$experiment_coord"
        mkdir -p "$target_dir"

        # Find the gatling timestamp folder
        gatling_folder=$(find "$artifact_dir" -maxdepth 1 -name "$GATLING_PATTERN" -type d)

        if [[ -n "$gatling_folder" ]]; then
            cp -r "$gatling_folder" "$target_dir/"
        else
            echo "Warning: No $GATLING_PATTERN folder found in $artifact_dir"
        fi

        # convert binary simulation.log to simulation.csv
        glog --config src/test/resources/gatling.conf --scan-subdirs "$target_dir"
    fi
done

echo "Pre-processing complete in: $ANALYSIS_DIR"
