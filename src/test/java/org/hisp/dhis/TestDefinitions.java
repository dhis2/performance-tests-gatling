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

import static io.gatling.javaapi.core.CoreDsl.constantConcurrentUsers;
import static io.gatling.javaapi.core.CoreDsl.rampUsers;
import static io.gatling.javaapi.core.CoreDsl.rampUsersPerSec;
import static io.gatling.javaapi.http.HttpDsl.http;
import static org.hisp.dhis.ConfigLoader.CONFIG;

import io.gatling.javaapi.core.ClosedInjectionStep;
import io.gatling.javaapi.core.OpenInjectionStep;
import io.gatling.javaapi.http.HttpProtocolBuilder;
import java.time.Duration;

/**
 * Provides the common definitions and settings used across all tests. It's the class where all
 * common settings should be defined.
 */
public class TestDefinitions {
  public static final String DHIS2_INSTANCE = CONFIG.getString("instance");
  public static final Double DHIS2_VERSION = CONFIG.getDouble("version", 0);
  public static final String USERNAME = CONFIG.getString("username");
  public static final String PASSWORD = CONFIG.getString("password");
  public static final String SCENARIO = CONFIG.getString("scenario");

  public static ClosedInjectionStep constantSingleUser(int during) {
    return constantConcurrentUsers(1).during(during);
  }

  public static OpenInjectionStep simpleUsersRumpUp(int users, int during) {
    return rampUsers(users).during(during);
  }

  public static OpenInjectionStep complexUsersRumpUp() {
    int totalDesiredUserCount = 15;
    double userRampUpPerInterval = 1;
    double rampUpIntervalSeconds = 3;

    int totalRampUptimeSeconds = 3;
    int steadyStateDurationSeconds = 20;

    return rampUsersPerSec(userRampUpPerInterval / (rampUpIntervalSeconds / 60))
        .to(totalDesiredUserCount)
        .during(Duration.ofSeconds(totalRampUptimeSeconds + steadyStateDurationSeconds));
  }

  public static HttpProtocolBuilder configureSimulationProtocol() {
    System.out.println("# Pointing to instance: " + DHIS2_INSTANCE);

    return http.baseUrl(DHIS2_INSTANCE)
        .acceptHeader("application/json")
        .maxConnectionsPerHost(100)
        .basicAuth(USERNAME, PASSWORD)
        .header("Content-Type", "application/json")
        .userAgentHeader("Gatling/Performance Test: " + DHIS2_INSTANCE);
  }
}
