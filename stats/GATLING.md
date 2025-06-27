# Gatling

## Data

Gatling records HTTP request timings during performance test runs. An example of the HTML report,
the binary simulation.log and the parsed simulation.csv are in
../samples/trackerexportertests-20250627064559771.

- Gatling uses the T-Digest algorithm (com.tdunning:t-digest library) during report generation
- Raw response times from simulation.log are fed into T-Digest data structures
- Percentiles (50th, 75th, 95th, 99th) are computed on-demand using digest.quantile(rank)
- happens in PercentilesBuffers.scala:40-49 in the gatling-charts module

We have access to the textual representation of simulation.log in simulation.csv. What we do not
have is the percentile data as that is calculated by Gatling and put into the HTML report.

Goal is
* write a python CLI in this directory
* that takes a report directory as input
* looks for simulation.csv
* calculates the percentile data like Gatling does
* reproduce ./response-time-stats.png from the HTML report printed as CSV to the console
* ignore KO for now, so assume all requests were OK (successful)
* ignore calculating the mean and std deviation

The following lists the record types that are in simulation.csv. You will need to filter for
`record_type=request` and group the data by `request_name` in case multiple HTTP requests to
different endpoints are contained.

### Record Types

**Request Records** (`record_type=request`):
- `group_hierarchy`: Pipe-separated group names (e.g., "Group1|SubGroup")
- `request_name`: HTTP request name/URL
- `status`: "OK" or "KO"
- `start_timestamp`/`end_timestamp`: Unix timestamps in milliseconds
- `response_time_ms`: Response time in milliseconds
- `error_message`: Error description (if any)
- `is_incoming`: "true" for unmatched incoming events, "false" for regular requests

```sh
grep request results.csv | head -2
```

**User Records** (`record_type=user`):
- `scenario_name`: Name of the scenario
- `event_type`: "start" or "end"
- `start_timestamp`: Unix timestamp in milliseconds

```sh
head -1 results.csv;grep user results.csv | head -2
```

**Group Records** (`record_type=group`):
- `group_hierarchy`: Pipe-separated group names
- `status`: "OK" or "KO"
- `start_timestamp`/`end_timestamp`: Unix timestamps in milliseconds
- `duration_ms`: Group duration in milliseconds
- `cumulated_response_time_ms`: Sum of response times

```sh
head -1 results.csv;grep group, results.csv | head -1
```

**Error Records** (`record_type=error`):
- `error_message`: Error description
- `start_timestamp`: Unix timestamp in milliseconds

