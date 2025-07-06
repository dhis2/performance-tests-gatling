#!/bin/bash
# get latest runs and convert binary simulation.log to simulation.csv

# Check if DEST_DIR parameter is provided
if [ $# -eq 0 ]; then
    echo "Usage: $0 <DEST_DIR>"
    echo "DEST_DIR parameter is required (e.g., experiment-raw-speed-tests)"
    exit 1
fi

DEST_DIR="$1"

# only get new files which allows us to run `mvn clean` on the host after each batch of tests
# without deleting any test reports we already synced
rsync --checksum --human-readable --recursive --times --compress --stats \
  ivo@test.performance.dhis2.org:/home/ivo/performance-tests-gatling/target/gatling/ \
  "$DEST_DIR"

# Run glog on dest_dir and its first level directories
glog --config src/test/resources/gatling.conf --scan-subdirs "$DEST_DIR"

# Run glog on each first-level subdirectory
for dir in "$DEST_DIR"/*/; do
    if [ -d "$dir" ]; then
        glog --config src/test/resources/gatling.conf --scan-subdirs "$dir"
    fi
done

# Test: verify that the number of simulation.log files equals the number of simulation.csv files
log_count=$(find "$DEST_DIR" -name simulation.log | wc -l)
csv_count=$(find "$DEST_DIR" -name simulation.csv | wc -l)

if [ "$log_count" -eq "$csv_count" ]; then
    echo "✓ Test passed: Found $log_count simulation.log files and $csv_count simulation.csv files"
else
    echo "✗ Test failed: Found $log_count simulation.log files but $csv_count simulation.csv files"
    exit 1
fi
