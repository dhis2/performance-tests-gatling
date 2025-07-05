#!/bin/bash
# Run a single GetRawSpeedTest scenario on the test.performance.dhis2.org server to compare actual
# results against previous claims and look at variability.
# Run without name resolution like:
#
# ./experiment-raw-speed-tests-run.sh -Dinstance=http://127.0.0.1:8103/42.0_hmis -Dversion=42.0.0 -Dbaseline=41.0.0 -Dgatling.resultsFolder=target/gatling/42.0_hmis
#
# To find the tomcat port for the DHIS2 instance you are looking for you can do (there might be better
# ways):
#
# ps aux | grep tomcat
# sudo netstat -a -p -n | grep 498564
#
# (it is likely an 8xxx port)

RUNS=24

mvn clean
for ((i=1; i<=RUNS; i++)); do
    echo "Running test iteration $i/$RUNS"
    mvn gatling:test \
     -Dgatling.simulationClass=org.hisp.dhis.test.GetRawSpeedTest \
     -Dscenario=test-scenarios/hmis/analytics-en-query-4-speed-get-test.json \
     "$@"

    if [ "$i" -lt "$RUNS" ]; then
        echo "Waiting 5 minutes before next test..."
        sleep 5m
    fi
done

