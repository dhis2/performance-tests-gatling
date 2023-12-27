#! /usr/bin/bash

readonly BASE_URL=http://127.0.0.1/2.38dev #http://localhost:8080/dhis
readonly USERNAME=admin
readonly PASSWORD=district

echo "Executing tests..."

mvn clean gatling:test -Dgatling.simulationClass=org.hisp.dhis.test.GetRawSpeedTest -Dinstance=$BASE_URL -Dscenario=test-cases/hmis/analytics-en-query-speed-get-test.json;
mvn gatling:test -Dgatling.simulationClass=org.hisp.dhis.test.GetRawSpeedTest -Dinstance=$BASE_URL -Dscenario=test-cases/hmis/analytics-ev-aggregate-speed-get-test.json;
mvn gatling:test -Dgatling.simulationClass=org.hisp.dhis.test.GetRawSpeedTest -Dinstance=$BASE_URL -Dscenario=test-cases/hmis/analytics-ev-query-speed-get-test.json;
mvn gatling:test -Dgatling.simulationClass=org.hisp.dhis.test.GetRawSpeedTest -Dinstance=$BASE_URL -Dscenario=test-cases/hmis/analytics-speed-get-test.json;
mvn gatling:test -Dgatling.simulationClass=org.hisp.dhis.test.GetRawSpeedTest -Dinstance=$BASE_URL -Dscenario=test-cases/hmis/analytics-te-query-speed-get-test.json;
mvn gatling:test -Dgatling.simulationClass=org.hisp.dhis.test.GetRawSpeedTest -Dinstance=$BASE_URL -Dscenario=test-cases/hmis/outliers-speed-get-test.json;
mvn gatling:test -Dgatling.simulationClass=org.hisp.dhis.test.GetRawSpeedTest -Dinstance=$BASE_URL -Dscenario=test-cases/hmis/system-speed-get-test.json;
mvn gatling:test -Dgatling.simulationClass=org.hisp.dhis.test.GetRawSpeedTest -Dinstance=$BASE_URL -Dscenario=test-cases/hmis/tracker-speed-get-test.json;

echo "Finished!"
