#! /usr/bin/bash

readonly BASE_URL=http://127.0.0.1/2.41dev #http://localhost:8080/dhis

echo "Executing tests..."

mvn clean gatling:test -Dgatling.simulationClass=org.hisp.dhis.test.GetRawSpeedTest -Dinstance=$BASE_URL -Dscenario=test-scenarios/hmis/analytics-en-query-speed-get-test.json;
mvn gatling:test -Dgatling.simulationClass=org.hisp.dhis.test.GetRawSpeedTest -Dinstance=$BASE_URL -Dscenario=test-scenarios/hmis/analytics-ev-aggregate-speed-get-test.json;
mvn gatling:test -Dgatling.simulationClass=org.hisp.dhis.test.GetRawSpeedTest -Dinstance=$BASE_URL -Dscenario=test-scenarios/hmis/analytics-ev-query-speed-get-test.json;
mvn gatling:test -Dgatling.simulationClass=org.hisp.dhis.test.GetRawSpeedTest -Dinstance=$BASE_URL -Dscenario=test-scenarios/hmis/analytics-speed-get-test.json;
mvn gatling:test -Dgatling.simulationClass=org.hisp.dhis.test.GetRawSpeedTest -Dinstance=$BASE_URL -Dscenario=test-scenarios/hmis/analytics-te-query-speed-get-test.json;
mvn gatling:test -Dgatling.simulationClass=org.hisp.dhis.test.GetRawSpeedTest -Dinstance=$BASE_URL -Dscenario=test-scenarios/hmis/analytics-outliers-speed-get-test.json;
mvn gatling:test -Dgatling.simulationClass=org.hisp.dhis.test.GetRawSpeedTest -Dinstance=$BASE_URL -Dscenario=test-scenarios/hmis/system-speed-get-test.json;
mvn gatling:test -Dgatling.simulationClass=org.hisp.dhis.test.GetRawSpeedTest -Dinstance=$BASE_URL -Dscenario=test-scenarios/hmis/tracker-speed-get-test.json;

echo "Finished!"
