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
package org.hisp.dhis;

import static io.gatling.javaapi.core.CoreDsl.scenario;
import static io.gatling.javaapi.http.HttpDsl.http;
import static org.hisp.dhis.TestDefinitions.DHIS2_VERSION;
import static org.hisp.dhis.TestDefinitions.SCENARIO;
import static org.hisp.dhis.TestDefinitions.constantSingleUser;
import static org.hisp.dhis.TestDefinitions.defaultHttpProtocol;
import static org.slf4j.LoggerFactory.getLogger;

import com.fasterxml.jackson.databind.ObjectMapper;
import io.gatling.javaapi.core.PopulationBuilder;
import io.gatling.javaapi.core.ScenarioBuilder;
import java.net.MalformedURLException;
import java.net.URL;
import java.nio.file.Path;
import java.util.List;
import org.dhis.model.Scenario;
import org.dhis.model.Scenarios;
import org.dhis.model.Version;
import org.slf4j.Logger;

/** Provides helper methods specifically related to tests. */
public class TestHelper {
  private static final Logger logger = getLogger(TestHelper.class);

  private TestHelper() {}

  /**
   * Loads the list of scenarios from the scenario file specified in the "scenario" property.
   * Through the "config.properties" file or at runtime.
   *
   * @return the list of {@link Scenario}.
   */
  public static List<Scenario> loadTestQueries() {
    Scenarios urls;
    URL currentTestFile = localScenarioFile();

    if (currentTestFile == null) {
      try {
        currentTestFile = absoluteScenarioFile();
      } catch (MalformedURLException e) {
        logger.error("Scenario file not found.");
        throw new RuntimeException(e);
      }
    }

    try {
      ObjectMapper mapper = new ObjectMapper();
      urls = mapper.readValue(currentTestFile, Scenarios.class);
    } catch (Exception e) {
      logger.error("Cannot load scenario file.");
      throw new RuntimeException(e);
    }

    return urls.getScenarios();
  }

  /**
   * Checks if the given version is currently supported, based on the DHIS2_VERSION set.
   *
   * @param version the {@link Version} to be matched.
   * @return true if the version is supported, false otherwise.
   */
  public static boolean isVersionSupported(Version version) {
    if (version != null) {
      if (version.getMin() != null && DHIS2_VERSION < version.getMin()) {
        return false;
      }

      if (version.getMax() != null && DHIS2_VERSION > version.getMax()) {
        return false;
      }
    }

    return true;
  }

  /**
   * Creates a {@link PopulationBuilder} with a fake scenario, pointing to localhost. No assertions
   * will be defined.
   *
   * @return the {@link PopulationBuilder} with the fake scenario.
   */
  public static PopulationBuilder fakePopulationBuilder() {
    ScenarioBuilder sb = scenario("Fake test (for unsupported)...").exec(http("localhost").get(""));
    return sb.injectClosed(constantSingleUser(1)).protocols(defaultHttpProtocol());
  }

  /**
   * Loads the current scenario file, relative to the local "test/resources" folder.
   *
   * @return the {@link URL} of the scenario file.
   */
  private static URL localScenarioFile() {
    return TestDefinitions.class.getClassLoader().getResource(SCENARIO);
  }

  /**
   * Loads the current scenario from a given absolute path.
   *
   * @return the {@link URL} of the scenario file.
   */
  private static URL absoluteScenarioFile() throws MalformedURLException {
    return Path.of(SCENARIO).toUri().toURL();
  }
}
