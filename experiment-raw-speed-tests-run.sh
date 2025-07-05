#!/bin/bash
# run a single GetRawSpeedTest scenario on the test.performance.dhis2.org server to compare actual
# results against previous claims and look at variability
#
# To find the tomcat port for the DHIS2 instance you are looking for you can do (there might be better
# ways)
# ps aux | grep tomcat
# sudo netstat -a -p -n | grep 498564
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

