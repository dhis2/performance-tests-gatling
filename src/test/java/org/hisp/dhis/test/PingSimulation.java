package org.hisp.dhis.test;

import static io.gatling.javaapi.core.CoreDsl.*;
import static io.gatling.javaapi.http.HttpDsl.*;

import io.gatling.javaapi.core.*;
import io.gatling.javaapi.http.*;

public class PingSimulation extends Simulation {
    private static final String BASE_URL = System.getProperty("baseUrl", "http://localhost");
    private static final String ENDPOINT = "/api/ping";
    private static final int DURATION = Integer.parseInt(System.getProperty("duration", "30"));

    HttpProtocolBuilder httpProtocol =
        http.baseUrl(BASE_URL)
            .acceptHeader("application/json")
            .contentTypeHeader("application/json");

    ScenarioBuilder testScenario = scenario("Response time test for GET /api/ping")
        .exec(
            http("api-ping")
                .get(ENDPOINT)
                .check(status().is(200))
            );

    {
        System.out.println("BASE_URL: " + BASE_URL);
        System.out.println("DURATION: " + DURATION);

        setUp(
            testScenario.injectClosed(
                constantConcurrentUsers(1).during(DURATION)
            ).protocols(httpProtocol)
        );
    }
}