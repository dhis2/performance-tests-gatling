#!/bin/sh
# TODO use one of them

mvn clean gatling:test -f ./performance-tests-gatling/pom.xml \
 -Dgatling.simulationClass=org.hisp.dhis.test.GetRawSpeedTest \
 -Dversion=42.0.0 -Dbaseline=41.0.0 -Dinstance=https://test.performance.dhis2.org/2.42_perf_test \
 -Dscenario=test-scenarios/hmis/analytics-speed-get-test.json > result.txt

mvn clean gatling:test -f ./performance-tests-gatling/pom.xml \
 -Dgatling.simulationClass=org.hisp.dhis.test.GetRawSpeedTest \
 -Dversion=42.0.0 -Dbaseline=41.0.0 -Dinstance=https://test.performance.dhis2.org/2.42_perf_test \
 -Dscenario=test-scenarios/hmis/analytics-en-query-speed-get-test.json > result.txt

mvn clean gatling:test -f ./performance-tests-gatling/pom.xml \
 -Dgatling.simulationClass=org.hisp.dhis.test.GetRawSpeedTest \
 -Dversion=42.0.0 -Dbaseline=41.0.0 -Dinstance=https://test.performance.dhis2.org/2.42_perf_test \
 -Dscenario=test-scenarios/hmis/analytics-ev-aggregate-speed-get-test.json > result.txt

mvn clean gatling:test -f ./performance-tests-gatling/pom.xml \
 -Dgatling.simulationClass=org.hisp.dhis.test.GetRawSpeedTest \
 -Dversion=42.0.0 -Dbaseline=41.0.0 -Dinstance=https://test.performance.dhis2.org/2.42_perf_test \
 -Dscenario=test-scenarios/hmis/analytics-ev-query-speed-get-test.json > result.txt

mvn clean gatling:test -f ./performance-tests-gatling/pom.xml \
 -Dgatling.simulationClass=org.hisp.dhis.test.GetRawSpeedTest \
 -Dversion=42.0.0 -Dbaseline=41.0.0 -Dinstance=https://test.performance.dhis2.org/2.42_perf_test \
 -Dscenario=test-scenarios/hmis/analytics-outliers-speed-get-test.json > result.txt

mvn clean gatling:test -f ./performance-tests-gatling/pom.xml \
 -Dgatling.simulationClass=org.hisp.dhis.test.GetRawSpeedTest \
 -Dversion=42.0.0 -Dbaseline=41.0.0 -Dinstance=https://test.performance.dhis2.org/2.42_perf_test \
 -Dscenario=test-scenarios/hmis/analytics-te-query-speed-get-test.json > result.txt

mvn clean gatling:test -f ./performance-tests-gatling/pom.xml \
 -Dgatling.simulationClass=org.hisp.dhis.test.GetRawSpeedTest \
 -Dversion=42.0.0 -Dbaseline=41.0.0 -Dinstance=https://test.performance.dhis2.org/2.42_perf_test \
 -Dscenario=test-scenarios/hmis/system-speed-get-test.json > result.txt

# grep ' : false (actual' result.txt

