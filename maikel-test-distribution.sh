#!/bin/bash
# gather some more runs to look at the distribution and at the variability

for i in {1..10}; do
    echo "Running test iteration $i/10"
    mvn gatling:test \
     -Dgatling.simulationClass=org.hisp.dhis.test.GetRawSpeedTest \
     -Dversion=42.0.0 -Dbaseline=41.0.0 -Dinstance=https://test.performance.dhis2.org/42.0_hmis \
     -Dscenario=test-scenarios/hmis/analytics-en-query-4-speed-get-test.json

    if [ $i -lt 10 ]; then
        echo "Waiting 1 minute before next test..."
        sleep 60
    fi
done

