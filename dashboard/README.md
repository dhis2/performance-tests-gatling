## Gatling Benchmarks Dashboard

Interactive, static dashboard for visualizing Gatling performance test results stored in this repository. It renders horizontal bar charts (with min/mean/max error bars) per query across DHIS2 releases and lets you deep-link to specific suites.

### Quick start

- **Serve the folder over HTTP** (opening the file directly in a browser may fail due to CORS when loading JSON):

  ```bash
  # from the root of the repository
  python3 -m http.server 8050
  ```

  Then open `http://localhost:8050/dashboard/` in your browser.

- You can use any static server (e.g., `npx serve`, `http-server`, Nginx). The only requirement is that the repository root is the web root so relative paths resolve. The port is configurable, of course.

### How it works

- The sidebar is built from `dashboard/data/test_structure.json`, which maps logical database names to test suite result files.
- When you pick a suite, the app loads the corresponding JSON from `src/test/resources/test-scenarios/<db>/<file>.json` and renders charts with Plotly.
- The page URL is updated with query parameters so you can share deep links.

### URL parameters

- **db**: database key from `test_structure.json` (e.g., `hmis`, `sierra-leone`)
- **suite**: test suite key under that database (e.g., `system-speed-get`)

Example:

  ```text
  index.html?db=sierra-leone&suite=system-speed-get
  ```

### Files of interest

- `dashboard/index.html`: page shell; includes D3 v7 and Plotly 2.27 via CDN
- `dashboard/js/main.js`: navigation, loading of test data, and rendering entrypoint
- `dashboard/js/visualization_plotly.js`: Plotly chart construction
- `dashboard/css/style.css`: styles
- `dashboard/data/test_structure.json`: lists databases and their suites
- `src/test/resources/test-scenarios/<db>/*.json`: actual suite result files

### `test_structure.json` format

This file declares which result file belongs to each suite. Keys under `databases` are used as URL `db` values; nested keys are used as `suite` values.

  ```json
  {
    "databases": {
      "hmis": {
        "analytics-speed-get": "analytics-speed-get-test.json",
        "system-speed-get": "system-speed-get-test.json"
      },
      "sierra-leone": {
        "system-speed-get": "system-speed-get-test.json"
      }
    }
  }
  ```

### Expected suite result JSON schema

Each suite result file must provide a `scenarios` array. The dashboard uses these fields:

- **query**: full request path and query string (shown above each chart)
- **expectations**: array of measurements per release
  - **release**: label such as `v40`, `v41`, ... (used for color and axis)
  - **mean**: mean response time in milliseconds
  - **min**: minimum response time in milliseconds
  - **max**: maximum response time in milliseconds

Minimal example:

  ```json
  {
    "scenarios": [
      {
        "query": "/api/analytics?dimension=dx:abc;def&filter=pe:THIS_YEAR",
        "expectations": [
          { "release": "v40", "mean": 210, "min": 180, "max": 260 },
          { "release": "v41", "mean": 190, "min": 170, "max": 230 }
        ]
      },
      {
        "query": "/api/system/info",
        "expectations": [
          { "release": "v40", "mean": 45, "min": 30, "max": 70 },
          { "release": "v41", "mean": 40, "min": 28, "max": 65 }
        ]
      }
    ]
  }
  ```

### Add a new database or suite

1. Place the new result file at `src/test/resources/test-scenarios/<db>/<your-file>.json`.
2. Add or update the mapping in `dashboard/data/test_structure.json`:

   - Add the `<db>` object if it does not exist
   - Inside it, add a new key for your suite and map to the filename

   Example:

  ```json
  {
    "databases": {
      "my-db": {
        "my-suite": "my-suite-test.json"
      }
    }
  }
  ```

3. Reload the dashboard. The suite should appear in the sidebar.

### Troubleshooting

- **Blank page or “Error loading test structure”**:
  - Ensure you’re serving via HTTP (not opening `file://`); start a local server as shown above
  - Confirm `dashboard/data/test_structure.json` is valid JSON

- **“Error loading test suite data”**:
  - Verify the filename mapped in `test_structure.json` exists under `src/test/resources/test-scenarios/<db>/`
  - Check the suite result JSON matches the expected schema

- **404s for JSON files**:
  - Your server root must be the repository root so relative paths resolve


### Tech notes

- Libraries: D3 v7 and Plotly 2.27 are loaded from CDNs in `index.html`
- Colors: versions/releases are assigned colors dynamically
- Query parameters view: toggle with the “Show/Hide Query Parameters” button at the top


