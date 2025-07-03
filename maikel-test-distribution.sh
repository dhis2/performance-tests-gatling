#!/bin/bash

mvn clean
# TODO repeat this every 20 times
mvn gatling:test \
 -Dgatling.simulationClass=org.hisp.dhis.test.GetRawSpeedTest \
 -Dversion=42.0.0 -Dbaseline=41.0.0 -Dinstance=https://test.performance.dhis2.org/42.0_hmis \
 -Dscenario=test-scenarios/hmis/analytics-en-query-4-speed-get-test.json

