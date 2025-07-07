#!/bin/bash
# Run TrackerExporterTests simulation on the test.performance.dhis2.org server to investigate
# variability when running them inside of Docker.
# Run like:
#
# ./experiment-tracker-exporter-tests-run-docker.sh -Dgatling.resultsFolder=target/gatling/42.0_sl_docker

cleanup() {
   echo ""
   echo "CTRL+C pressed, clean up things before exiting..."
   exit 1 # this is only ok as I don't care for other scripts calling this script
}

trap cleanup SIGINT

RUNS=24

mvn clean

# https://test.performance.dhis2.org/42.0_sl uses this DB
# performance/2.39.6-analytics-be-dhis2-db-sierra-leone.sql.gz
# not sure how it differs from the DHIS2_DB_DUMP_URL one
DHIS2_IMAGE=dhis2/core:42.0 \
DHIS2_DB_DUMP_URL=https://databases.dhis2.org/sierra-leone/2.42.0/dhis2-db-sierra-leone.sql.gz \
docker compose up --detach --remove-orphans db

for ((i=1; i<=RUNS; i++)); do
  echo "Running test iteration $i/$((RUNS+1))"
    DHIS2_IMAGE=dhis2/core:42.0 \
    docker compose up --force-recreate --detach web
    echo "Waiting for DHIS2 to start..."
    timeout 300 bash -c 'until docker compose ps web | grep -q "healthy"; do sleep 10; echo "Still waiting..."; done'
    echo "DHIS2 is ready!"

    mvn gatling:test \
     -Dgatling.simulationClass=org.hisp.dhis.test.TrackerExporterTests \
     "$@"

    # always start a new DHIS2 container
    docker compose rm --stop --force web

    if [ "$i" -lt "$RUNS" ]; then
      echo "Waiting 5 minutes before next run $((i+1))/$((RUNS+1))"
        sleep 5m
    fi
done

docker compose stop db
