#!/bin/bash
# gather some more runs to look at the distribution and at the variability

RUNS=24
for i in $(seq 1 $RUNS); do
    echo "Running test iteration $i/$RUNS"
    mvn gatling:test \
     -Dgatling.simulationClass=org.hisp.dhis.test.GetRawSpeedTest \
     -Dversion=42.0.0 -Dbaseline=41.0.0 -Dinstance=https://test.performance.dhis2.org/42.0_hmis \
     -Dscenario=test-scenarios/hmis/analytics-en-query-4-speed-get-test.json

    if [ "$i" -lt "$RUNS" ]; then
        echo "Waiting 5 minutes before next test..."
        sleep 5m
    fi
done

