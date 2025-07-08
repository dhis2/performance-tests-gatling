#!/bin/bash
# Run TrackerExporterTests simulation on the test.performance.dhis2.org server to investigate
# variability when running them without Docker.
# Run without name resolution like:
#
# ./experiment-tracker-exporter-tests-run.sh -Dinstance=http://127.0.0.1:8103/42.0_sl -Dgatling.resultsFolder=target/gatling/42.0_sl_no_docker
#
# To find the tomcat port for the DHIS2 instance you are looking for you can do (there might be better
# ways):
#
# ps aux | grep 42.0_sl/tomcat
# sudo netstat -a -p -n | grep 498564
#
# (it is likely an 8xxx port)

RUNS=24

mvn clean
for ((i=1; i<=RUNS; i++)); do
  echo "Running test iteration $i/$((RUNS+1))"
    mvn gatling:test \
     -Dgatling.simulationClass=org.hisp.dhis.test.TrackerExporterTests \
     "$@"

    if [ "$i" -lt "$RUNS" ]; then
      echo "Waiting 5 minutes before next run $((i+1))/$((RUNS+1))"
        sleep 5m
    fi
done

