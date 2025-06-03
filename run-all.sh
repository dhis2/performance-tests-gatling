#! /usr/bin/bash

readonly BASE_URL=https://test.performance.dhis2.org/2.40.2.2 #http://localhost:8080/dhis
readonly VERSION=40.2.2
readonly BASELINE=40.2.2

echo "Executing tests..."

mvn clean gatling:test -Dgatling.simulationClass=org.hisp.dhis.test.GetRawSpeedTest -Dinstance=$BASE_URL -Dversion=$VERSION -Dbaseline=$BASELINE -Dscenario=test-scenarios/hmis/analytics-en-query-speed-get-test.json;
sleep 5; mvn gatling:test -Dgatling.simulationClass=org.hisp.dhis.test.GetRawSpeedTest -Dinstance=$BASE_URL -Dversion=$VERSION -Dbaseline=$BASELINE -Dscenario=test-scenarios/hmis/analytics-ev-aggregate-speed-get-test.json;
sleep 5; mvn gatling:test -Dgatling.simulationClass=org.hisp.dhis.test.GetRawSpeedTest -Dinstance=$BASE_URL -Dversion=$VERSION -Dbaseline=$BASELINE -Dscenario=test-scenarios/hmis/analytics-ev-query-speed-get-test.json;
sleep 5; mvn gatling:test -Dgatling.simulationClass=org.hisp.dhis.test.GetRawSpeedTest -Dinstance=$BASE_URL -Dversion=$VERSION -Dbaseline=$BASELINE -Dscenario=test-scenarios/hmis/analytics-speed-get-test.json;
sleep 5; mvn gatling:test -Dgatling.simulationClass=org.hisp.dhis.test.GetRawSpeedTest -Dinstance=$BASE_URL -Dversion=$VERSION -Dbaseline=$BASELINE -Dscenario=test-scenarios/hmis/analytics-te-query-speed-get-test.json;
sleep 5; mvn gatling:test -Dgatling.simulationClass=org.hisp.dhis.test.GetRawSpeedTest -Dinstance=$BASE_URL -Dversion=$VERSION -Dbaseline=$BASELINE -Dscenario=test-scenarios/hmis/analytics-outliers-speed-get-test.json;
sleep 5; mvn gatling:test -Dgatling.simulationClass=org.hisp.dhis.test.GetRawSpeedTest -Dinstance=$BASE_URL -Dversion=$VERSION -Dbaseline=$BASELINE -Dscenario=test-scenarios/hmis/system-speed-get-test.json;
sleep 5; mvn gatling:test -Dgatling.simulationClass=org.hisp.dhis.test.GetRawSpeedTest -Dinstance=$BASE_URL -Dversion=$VERSION -Dbaseline=$BASELINE -Dscenario=test-scenarios/hmis/tracker-speed-get-test.json;
sleep 5; mvn gatling:test -Dgatling.simulationClass=org.hisp.dhis.test.GetRawSpeedTest -Dinstance=$BASE_URL -Dversion=$VERSION -Dbaseline=$BASELINE -Dscenario=test-scenarios/sierra-leone/route-speed-run-test.json;

echo "Finished!"
