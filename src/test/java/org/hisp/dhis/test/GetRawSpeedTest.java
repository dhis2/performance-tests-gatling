/*
 * Copyright (c) 2004-2023, University of Oslo
 * All rights reserved.
 *
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions are met:
 * Redistributions of source code must retain the above copyright notice, this
 * list of conditions and the following disclaimer.
 *
 * Redistributions in binary form must reproduce the above copyright notice,
 * this list of conditions and the following disclaimer in the documentation
 * and/or other materials provided with the distribution.
 * Neither the name of the HISP project nor the names of its contributors may
 * be used to endorse or promote products derived from this software without
 * specific prior written permission.
 *
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
 * ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
 * WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
 * DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
 * ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
 * (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
 * LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
 * ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
 * (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
 * SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
 */
package org.hisp.dhis.test;

import static io.gatling.javaapi.core.CoreDsl.details;
import static io.gatling.javaapi.core.CoreDsl.scenario;
import static io.gatling.javaapi.http.HttpDsl.http;
import static io.gatling.javaapi.http.HttpDsl.status;
import static org.apache.commons.lang3.ObjectUtils.defaultIfNull;
import static org.hisp.dhis.TestDefinitions.configureSimulationProtocol;
import static org.hisp.dhis.TestDefinitions.constantSingleUser;
import static org.hisp.dhis.TestHelper.fakePopulationBuilder;
import static org.hisp.dhis.TestHelper.isVersionSupported;
import static org.hisp.dhis.TestHelper.loadTestQueries;
import static org.slf4j.LoggerFactory.getLogger;

import io.gatling.javaapi.core.Assertion;
import io.gatling.javaapi.core.PopulationBuilder;
import io.gatling.javaapi.core.ScenarioBuilder;
import io.gatling.javaapi.core.Simulation;
import java.util.ArrayList;
import java.util.List;
import org.dhis.model.Scenario;
import org.slf4j.Logger;

/**
 * This is a generic test class focused on GET queries only. Based on a given input file, defined at
 * runtime, it will execute all the queries and assert their respective expectations. The tests are
 * focused on testing the raw speed of each query.
 */
public class GetRawSpeedTest extends Simulation {
  private static final Logger logger = getLogger(GetRawSpeedTest.class);

  public GetRawSpeedTest() {
    List<Scenario> testQueries = loadTestQueries();
    List<PopulationBuilder> populationBuilders = new ArrayList<>();
    List<Assertion> assertions = new ArrayList<>();

    for (Scenario testQuery : testQueries) {
      String query = testQuery.getQuery();
      boolean hasExpectations = testQuery.getExpectations() != null;
      boolean versionMatches = isVersionSupported(testQuery.getVersion());

      if (hasExpectations && versionMatches) {
        // Define expectations.
        int min = defaultIfNull(testQuery.getExpectations().getMin(), 0);
        int max = defaultIfNull(testQuery.getExpectations().getMax(), 0);
        int mean = defaultIfNull(testQuery.getExpectations().getMean(), 0);

        // Build assertions.
        populationBuilders.add(populationBuilder(query));
        assertions.add(details(query).responseTime().min().gte(min));
        assertions.add(details(query).responseTime().max().lte(max));
        assertions.add(details(query).responseTime().mean().lte(mean));
        assertions.add(details(query).successfulRequests().percent().gte(100d));
      } else {
        logger.warn("Skipping query: {}", query);
      }
    }

    if (!populationBuilders.isEmpty()) {
      // Test and assert.
      setUp(populationBuilders).assertions(assertions);
    } else {
      // Skip unsupported queries avoiding a crash.
      setUp(fakePopulationBuilder());
    }
  }

  private PopulationBuilder populationBuilder(String query) {
    return scenarioBuilder(query)
        .injectClosed(constantSingleUser())
        .protocols(configureSimulationProtocol());
  }

  private ScenarioBuilder scenarioBuilder(String query) {
    logger.info(query);

    return scenario("Raw speed test for GET " + query)
        .exec(http(query).get(query).check(status().is(200)));
  }
}
