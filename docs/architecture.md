# Architecture

OpenCRE Terminal is static-first. The browser consumes versioned JSON and other generated files; it never connects to a production database or an application server.

```text
Public sources -> GitHub Actions pipelines -> JSON / Parquet datasets -> GitHub Pages -> React terminal
```

GitHub Actions will eventually fetch, validate, normalize, analyze, and publish datasets. Python and DuckDB may be used in those ephemeral workflows, but no database service is deployed. Secrets remain inside Actions and are never bundled into the frontend.

Phases 1 through 4 contain the frontend foundation, a deterministic synthetic-data pipeline, audited market analytics/rankings, and versioned signal definitions. The Python layer uses Polars and NumPy to generate, normalize, and score test records, then uses in-memory DuckDB to write and validate Parquet. It makes no API calls, starts no service, and retains no database file. Later phases will add public-data pipelines and an optional data-provider interface for legitimately licensed providers. No proprietary-data scraping, AI model, embedding system, or LLM integration is in scope.

## Frontend data contract

The frontend obtains data only through `src/data/client.ts`. Dataset paths are resolved relative to the Vite base path so local development and GitHub Pages use the same contract. Phase 1 ships `public/data/v1/dashboard.json`, whose records contain a `data_label` field identifying them as synthetic demo data.

## Deployment

The Pages workflow installs frontend dependencies, runs type checking and a production build, uploads `frontend/dist`, and deploys it with the minimum Pages permissions. Repository content writes are not required by the Phase 1 deployment workflow.

The `data-validation` workflow runs the Phase 2 generator and validator in an ephemeral GitHub Actions environment. It has read-only repository access and produces no persistent service or secret-dependent output.
