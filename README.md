# Performance tests
The performance tests are becoming extremely important as DHIS2 gets more visibility.
Each year users enter and store a large amount of data, while DHIS2 is gaining new and more complex features.
In this scenario, performance becomes a challenge.

Because of that, writing performance tests are crucial.

## Why Gatling?
- Easy to write tests (Java, Kotlin and Scala)
- Tests can be recorded/generated through a standalone tool
- Executes through Maven
- Easy to integrate into the build/deployment pipeline
- Good reports out-of-the-box
- Good performance (low memory and CPU footprint)
- Has a free version
- Modular and very suitable for API tests

## Project structure
The tests are organized as follows:
1) The `main/java` folder contains models and classes that can be used by the tests, but do not have any specific test configuration/definitions.
2) In the `test/java` folder we find the classes responsible for the actual execution of tests and any configuration/settings related to the tests.
3) The suite of test scenarios to be validated are found at `test/resources/test-scenarios`.
4) Configuration related to Gatling and tests themselves are located at `test/resources/gatling.conf` and `test/resources/config.properties` respectively.

# Adding and executing tests
The steps below should give you the necessary instructions to add a new test as well as how to execute them.
_Currently, we only support GET endpoints._

## Adding a new scenario file
Simply follow these steps:
1) Go to the folder `test/resources/test-scenarios`.
2) Find the database (folder) to be used by the scenarios (ie: `hmis`).
3) Add the new JSON file, that contains the scenarios, in the database folder.

**_If you need to add a new database folder, simply create a new one at the same level as others database folders._**

## Adding a new scenario to an existing file
This is very easy. Follow the steps below:
1) In `test/resources/test-scenarios` find the database you want to use and add a new scenario in the respective JSON file. ie: `test-scenarios/hmis/analytics-speed-get-test.json`.
2) Add a new scenario, including it in the respective JSON file, ie:
```
    {
      "query": "/api/analytics?dimension=dx:D6Z8vC4lHkk,pe:LAST_12_MONTHS&filter=ou:USER_ORGUNIT&displayProperty=NAME&includeNumDen=false&skipMeta=false&skipData=false&relativePeriodDate=2023-11-14",
      "expectations": {
        "min": 230,
        "max": 800,
        "mean": 565
      },
      "version": {
        "min": "38",
        "max": "41"
      }
    }
```
- _query_: the URL/endpoint to be tested.
- _expectations_: the response times expected.
- _version_: the minimum/maximum version where this URL/endpoint is valid and can be reached. Usually, only the minimum version is needed, unless there is a very good reason to set a maximum version.

## Pointing to an external scenario file
We can also point to external JSON scenario files that are living in the file system, outside this project.
This can be done by specifying the root path of the respective file through the `scenario` property in `config.properties`, or at execution time (`-Dscenario=/myFolder/myScenarioFile.json`).

## Executing the tests
The tests are run through Maven, using the `config.properties` definitions. Ie:
```
mvn clean gatling:test
```

All properties defined in `config.properties` can be overwritten (prefixing them with **-D**), if desirable, through the command line. Ie:
```
mvn clean gatling:test -Dgatling.simulationClass=org.hisp.dhis.test.GetRawSpeedTest -Dscenario=test-scenarios/hmis/analytics-en-query-speed-get-test.json -Dusername=anyName -Dpassword=anyPwd -Dversion=39
```

It's also possible running all tests together using the script `run-all.sh`, located at the root of the project.
**NOTE:** _This script contains a few variables that need to be set for each case/environment._

# Pre-requirements
- An immutable DHIS2 database (for consistent metrics/tests).
- Most tests are based on the database `hmis/2.38.4/qa_hmis.sql.gz`. It can be found at https://im.dhis2.org/databases (you might require additional permission).
- A dedicated DHIS2 instance to be hit by the performance tests (the tests will run against this instance).
