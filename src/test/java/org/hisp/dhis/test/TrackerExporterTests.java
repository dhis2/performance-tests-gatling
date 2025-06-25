/*
 * Copyright (c) 2004-2025, University of Oslo
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
import static org.hisp.dhis.TestDefinitions.constantSingleUser;
import static org.slf4j.LoggerFactory.getLogger;

import io.gatling.javaapi.core.ScenarioBuilder;
import io.gatling.javaapi.core.Simulation;
import io.gatling.javaapi.http.HttpProtocolBuilder;
import org.slf4j.Logger;

// TODO(ivo) is there a way to give the simulation a different name than the class name?
public class TrackerExporterTests extends Simulation {
  private static final Logger logger = getLogger(TrackerExporterTests.class);
  HttpProtocolBuilder httpProtocolBuilder =
      http.baseUrl("http://localhost:8080")
          .acceptHeader("application/json")
          .maxConnectionsPerHost(100)
          .basicAuth("admin", "district")
          .header("Content-Type", "application/json")
          .userAgentHeader("Gatling/Performance Test");

  public TrackerExporterTests() {
    // SL DB has ~424k events vs ~257k in HMIS DB
    // Event program: VBqh0ynB2wv Malaria Case Registration is the largest event program with ~200k
    // events
    String largeProgram = "VBqh0ynB2wv";
    // Event program: bMcwwoVnbSR Malaria testing and surveillance has ~10k events
    String smallProgram = "bMcwwoVnbSR";
    String program = System.getProperty("large") != null ? largeProgram : smallProgram;
    // TODO(ivo) get realistic query from Glowroot
    String query =
        "/api/tracker/events?program="
            + program
            + "&pageSize=100&totalPages=true&occurredAfter=2024-01-01&occurredBefore=2024-12-31";
    ScenarioBuilder scenario =
        scenario(query).exec(http("events").get(query).check(status().is(200)));

    setUp(scenario.injectClosed(constantSingleUser(15)))
        .protocols(httpProtocolBuilder)
        .assertions(
            details("events").successfulRequests().percent().gte(100d),
            details("events").responseTime().percentile(90).lte(5000));
  }
}
