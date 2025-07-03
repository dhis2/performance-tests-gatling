#!/bin/sh
# TODO use one of them

# mvn clean gatling:test -f ./performance-tests-gatling/pom.xml \
#  -Dgatling.simulationClass=org.hisp.dhis.test.GetRawSpeedTest \
#  -Dversion=42.0.0 -Dbaseline=41.0.0 -Dinstance=https://test.performance.dhis2.org/2.42_perf_test \
#  -Dscenario=test-scenarios/hmis/analytics-speed-get-test.json > result.txt

# test how the results vary
# TODO why use the FQDN when running tests on the instance using ssh?
mvn clean gatling:test \
 -Dgatling.simulationClass=org.hisp.dhis.test.GetRawSpeedTest \
 -Dversion=42.0.0 -Dbaseline=41.0.0 -Dinstance=https://test.performance.dhis2.org/2.42_perf_test \
 -Dscenario=test-scenarios/hmis/analytics-en-query-4-speed-get-test.json # | tee --apend result.txt

# mvn clean gatling:test -f ./performance-tests-gatling/pom.xml \
#  -Dgatling.simulationClass=org.hisp.dhis.test.GetRawSpeedTest \
#  -Dversion=42.0.0 -Dbaseline=41.0.0 -Dinstance=https://test.performance.dhis2.org/2.42_perf_test \
#  -Dscenario=test-scenarios/hmis/analytics-ev-aggregate-speed-get-test.json > result.txt
#
# mvn clean gatling:test -f ./performance-tests-gatling/pom.xml \
#  -Dgatling.simulationClass=org.hisp.dhis.test.GetRawSpeedTest \
#  -Dversion=42.0.0 -Dbaseline=41.0.0 -Dinstance=https://test.performance.dhis2.org/2.42_perf_test \
#  -Dscenario=test-scenarios/hmis/analytics-ev-query-speed-get-test.json > result.txt
#
# mvn clean gatling:test -f ./performance-tests-gatling/pom.xml \
#  -Dgatling.simulationClass=org.hisp.dhis.test.GetRawSpeedTest \
#  -Dversion=42.0.0 -Dbaseline=41.0.0 -Dinstance=https://test.performance.dhis2.org/2.42_perf_test \
#  -Dscenario=test-scenarios/hmis/analytics-outliers-speed-get-test.json > result.txt
#
# mvn clean gatling:test -f ./performance-tests-gatling/pom.xml \
#  -Dgatling.simulationClass=org.hisp.dhis.test.GetRawSpeedTest \
#  -Dversion=42.0.0 -Dbaseline=41.0.0 -Dinstance=https://test.performance.dhis2.org/2.42_perf_test \
#  -Dscenario=test-scenarios/hmis/analytics-te-query-speed-get-test.json > result.txt
#
# mvn clean gatling:test -f ./performance-tests-gatling/pom.xml \
#  -Dgatling.simulationClass=org.hisp.dhis.test.GetRawSpeedTest \
#  -Dversion=42.0.0 -Dbaseline=41.0.0 -Dinstance=https://test.performance.dhis2.org/2.42_perf_test \
#  -Dscenario=test-scenarios/hmis/system-speed-get-test.json > result.txt

# grep ' : false (actual' result.txt

