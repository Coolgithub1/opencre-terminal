# Architecture

OpenCRE Terminal is static-first. The browser consumes versioned JSON and other generated files; it never connects to a production database or an application server.

```text
Public sources -> GitHub Actions pipelines -> JSON / Parquet datasets -> GitHub Pages -> React terminal
```

GitHub Actions will eventually fetch, validate, normalize, analyze, and publish datasets. Python and DuckDB may be used in those ephemeral workflows, but no database service is deployed. Secrets remain inside Actions and are never bundled into the frontend.

Phases 1 through 4 contain the frontend foundation, a deterministic synthetic-data pipeline, audited market analytics/rankings, and versioned signal definitions. The Python layer uses Polars and NumPy to generate, normalize, and score test records, then uses in-memory DuckDB to write and validate Parquet. It makes no API calls, starts no service, and retains no database file. Later phases will add public-data pipelines and an optional data-provider interface for legitimately licensed providers. No proprietary-data scraping, AI model, embedding system, or LLM integration is in scope.

## Frontend data contract

The frontend obtains data only through `src/data/client.ts`. Dataset paths are resolved relative to the Vite base path so local development and GitHub Pages use the same contract. Each default pipeline run copies generated `data/` files to `frontend/public/data/v1/` before the Vite build. The dashboard uses compact current datasets, while a signal chart fetches only the selected market's 50-record history file. Every record carries a `data_label` identifying it as synthetic demo data.

## Deployment

The Pages workflow runs the deterministic Python pipeline, installs frontend dependencies, runs type checking and a production build, uploads `frontend/dist`, and deploys it with the minimum Pages permissions. Repository content writes are not required by the deployment workflow.

The `data-validation` workflow runs the Phase 2 generator and validator in an ephemeral GitHub Actions environment. It has read-only repository access and produces no persistent service or secret-dependent output.

## Phase 6 geography

The generator writes one static `geography/markets.geojson` FeatureCollection, with a representative city-centroid point for each synthetic market. The browser loads that small file only when the Map page opens and joins it to the current static signals and analytics in memory. MapLibre renders an intentionally empty terminal background and point layers; it requests no tiles, uses no map token or third-party mapping API, and requires no spatial database. Points never represent legal market, MSA, submarket, property, county, ZIP, or census boundaries.
