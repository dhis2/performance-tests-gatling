# Performance tests

The performance tests are becoming extremely important as DHIS2 gets more visibility.
Each year users enter and store a large amount of data, while DHIS2 is gaining new and more complex
features.
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

1) The `main/java` folder contains models and classes that can be used by the tests, but do not have
   any specific test configuration/definitions.
2) In the `test/java` folder we find the classes responsible for the actual execution of tests and
   any configuration/settings related to the tests.
3) The suite of test scenarios to be validated are found at `test/resources/test-scenarios`.
4) Configuration related to Gatling and tests themselves are located
   at `test/resources/gatling.conf` and `test/resources/config.properties` respectively.

# Adding and executing tests

The steps below should give you the necessary instructions to add a new test as well as how to
execute them.
_Currently, we only support GET endpoints._

## Adding a new scenario file

Simply follow these steps:

1) Go to the folder `test/resources/test-scenarios`.
2) Find the database (folder) to be used by the scenarios (ie: `hmis`).
3) Add the new JSON file, that contains the scenarios, in the database folder.

**_If you need to add a new database folder, simply create a new one at the same level as others
database folders._**

## Adding a new scenario to an existing file

This is very easy. Follow the steps below:

1) In `test/resources/test-scenarios` find the database you want to use and add a new scenario in
   the respective JSON file. ie: `test-scenarios/hmis/analytics-speed-get-test.json`.
2) Add a new scenario, including it in the respective JSON file, ie:

```
    {
      "query": "/api/analytics?dimension=dx:D6Z8vC4lHkk,pe:LAST_12_MONTHS&filter=ou:USER_ORGUNIT&displayProperty=NAME&includeNumDen=false&skipMeta=false&skipData=false&relativePeriodDate=2023-11-14",
      "expectations": [
        {
          "release": "41.0",
          "min": 85,
          "max": 220,
          "mean": 150
        },
        {
          "release": "40.2.2",
          "min": 85,
          "max": 220,
          "mean": 150
        }
      ],
      "version": {
        "min": "40.1",
        "max": "41.0"
      }
    }
```

- _query_: the URL/endpoint to be tested.
- _expectations_: the response times expected for the targeted releases.
- _version_: the minimum/maximum version where this URL/endpoint is valid and can be reached.
  Usually, only the minimum version is needed, unless there is a very good reason to set a maximum
  version.

## Pointing to an external scenario file

We can also point to external JSON scenario files that are living in the file system, outside this
project.
This can be done by specifying the root path of the respective file through the `scenario` property
in `config.properties`, or at execution time (`-Dscenario=/myFolder/myScenarioFile.json`).

## Executing the tests

**NOTE:** _Before executing any test, ensure that a FULL vacuum was run on the current database.
This will provide more consistency during the executions._

Ensure the repository was cloned in the local machine:

```
git clone https://github.com/dhis2/performance-tests-gatling.git
```

Then `cd` into the project's directory:

```
cd performance-tests-gatling
```

Finally, the tests are run through Maven, using the `config.properties` definitions. Ie:

```
mvn clean gatling:test
```

The above will take the default directory defined, in `pom.xml`, for the test simulation. See

```
<simulationsFolder>${project.basedir}/src/test/java/org/hisp/dhis/analytics/get</simulationsFolder>
```

Note that all properties defined in `config.properties` can be overwritten (prefixing them with **-D
**), if desirable, through the command line. Ie:

```
mvn clean gatling:test -Dgatling.simulationClass=org.hisp.dhis.test.GetRawSpeedTest -Dscenario=test-scenarios/hmis/analytics-en-query-speed-get-test.json -Dusername=anyName -Dpassword=anyPwd -Dversion=39.4 -Dbaseline=41.0 -Dinstance=https://test.performance.dhis2.org/2.39dev
```

(In the example above we are forcing a single specific scenario:
***Dgatling.simulationClass=class***).

It's also possible running all tests together using the script `run-all.sh`, located at the root of
the project.
**NOTE:** _This script contains a few variables that need to be set for each case/environment._

### Supported properties

| Property           | Description                                                                                                                                                                           |
|--------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| gatling.simulation | The target simulation class.                                                                                                                                                          |
| instance           | The instance/server of DHIS2 that tests will hit.                                                                                                                                     |
| version            | The version of the DHIS2 server instance.                                                                                                                                             |
| baseline           | The DHIS2 version to be used as baseline for the test expectations.                                                                                                                   |
| scenario           | Test suite/scenario to be executed (refers to a respective file name). It can be relative to the internal folder "test-scenarios" or an absolute path.                                |
| query              | Forces the execution of a specific single query. All others will be ignored, except this one. Double quotes (") must be used so it can read correctly. ie.: -Dquery="/api/test?arg=1" |
| username           | Username of the target DHIS2 server to be used during the tests.                                                                                                                      |
| password           | Password for the username.                                                                                                                                                            |

# Pre-requirements

- An immutable DHIS2 database (for consistent metrics/tests).
- Most tests are based on the database `hmis/2.38.4/qa_hmis.sql.gz`. It can be found
  at https://im.dhis2.org/databases (you might require additional permission).
- A dedicated DHIS2 instance to be hit by the performance tests (the tests will run against this
  instance).
- Java JDK 11 or later
- Maven 3.6 or later
