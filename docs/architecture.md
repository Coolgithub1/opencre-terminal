# Architecture

OpenCRE Terminal is static-first. The browser consumes versioned JSON and other generated files; it never connects to a production database or an application server.

```text
Public sources -> GitHub Actions pipelines -> JSON / Parquet datasets -> GitHub Pages -> React terminal
```

GitHub Actions will eventually fetch, validate, normalize, analyze, and publish datasets. Python and DuckDB may be used in those ephemeral workflows, but no database service is deployed. Secrets remain inside Actions and are never bundled into the frontend.

Phases 1 through 8 contain the frontend foundation, deterministic synthetic data, audited market analytics/rankings, versioned signal definitions, static geography, rule-based RSS events, and a deterministic economic baseline. The Python layer uses Polars and NumPy to generate, normalize, and score test records, then uses in-memory DuckDB to write and validate Parquet. It makes no API calls during the deterministic Pages build, starts no service, and retains no database file. The separate RSS and credential-aware economic workflows make narrowly scoped public-source requests and write ephemeral artifacts only. No proprietary-data scraping, AI model, embedding system, or LLM integration is in scope.

## Frontend data contract

The frontend obtains data only through `src/data/client.ts`. Dataset paths are resolved relative to the Vite base path so local development and GitHub Pages use the same contract. Each default pipeline run copies generated `data/` files to `frontend/public/data/v1/` before the Vite build. The dashboard uses compact current datasets, while a signal chart fetches only the selected market's 50-record history file. Every record carries a `data_label` identifying it as synthetic demo data.

## Deployment

The Pages workflow runs the deterministic Python pipeline, installs frontend dependencies, runs type checking and a production build, uploads `frontend/dist`, and deploys it with the minimum Pages permissions. Repository content writes are not required by the deployment workflow.

The `data-validation` workflow runs the Phase 2 generator and validator in an ephemeral GitHub Actions environment. It has read-only repository access and produces no persistent service or secret-dependent output.

## Phase 6 geography

The generator writes one static `geography/markets.geojson` FeatureCollection, with a representative city-centroid point for each synthetic market. The browser loads that small file only when the Map page opens and joins it to the current static signals and analytics in memory. MapLibre renders an intentionally empty terminal background and point layers; it requests no tiles, uses no map token or third-party mapping API, and requires no spatial database. Points never represent legal market, MSA, submarket, property, county, ZIP, or census boundaries.

## Phase 7 RSS events

The terminal's generated `events/articles.json`, `events/extracted.json`, and `events/latest.json` use a deterministic synthetic RSS fixture so every Pages build remains reproducible. The event engine matches configured phrases, canonical entity aliases, and market-name dictionaries; an event is dropped if an entity or market is ambiguous. It fetches neither article pages nor any full-text content.

The separate `rss-ingestion.yml` workflow runs every 30 minutes and reads only reviewed publisher RSS XML endpoints from `pipelines/rss/feeds.json`. It creates a short-lived Actions artifact rather than changing the deployed bundle, which keeps live public metadata distinct from the clearly labeled demo terminal until source-level review and release governance are added. It has read-only repository permissions and no secrets.

## Phase 8 public economics

The deterministic build writes a five-series synthetic United States economic dataset for the dashboard. `economic/history.parquet` preserves 50 monthly points per series and `economic/latest.json` is the compact browser payload. Both carry the same demo label and provenance fields as the rest of the bundle.

`economic-data.yml` is a separately scheduled, read-only workflow. It can access BLS, Census, FRED, and SEC connector credentials through Actions secrets, then retains only normalized public records and connector health as a seven-day artifact. It never writes live source data to the repository or Pages bundle. Missing credentials return `skipped` without calling the source; configured-source failures are reported per connector without preventing the others from running.

## Phase 9 backtesting

The deterministic pipeline joins a synthetic signal observation to the same synthetic market's future rent-growth observation at a 3-, 6-, or 12-month offset. It materializes a small selection grid covering each market, each asset class, and the total universe at thresholds 50, 60, and 70. The React page only filters this 234-record JSON file; it does not calculate outcomes in the browser or contact a service. The standalone workflow reproduces it as a short-lived read-only artifact.
