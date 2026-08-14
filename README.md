# OpenCRE Terminal

OpenCRE Terminal is an open-source, static-first commercial real estate intelligence terminal. It is designed to run entirely through GitHub Pages and GitHub Actions, without a server, database, paid AI service, or proprietary data dependency.

## Current status

Phases 1 through 6 are complete. The project includes a Vite + React + TypeScript terminal shell, GitHub Pages deployment, reproducible static datasets, deterministic market analytics/rankings, configurable signals with complete score decompositions, interactive terminal charts/tables, and a MapLibre market-signal map. All provided datasets and displayed numbers are explicitly labeled **DEMO DATA — synthetic, not real market data**. Map points are representative city centroids, not market or administrative boundaries.

## Phase 6: static geography

Phase 6 adds an on-demand MapLibre signal view backed by a versioned 20-feature GeoJSON collection. These are representative city-centroid points for synthetic demo markets, not market, MSA, property, or administrative boundaries. The terminal map uses an empty local style and no map tiles, token, mapping API, spatial database, or application server.

## Local development

```bash
cd frontend
npm install
npm run dev
```

Generate and validate the static demo datasets:

```bash
python -m pip install -r requirements.txt
python scripts/run_pipeline.py
python scripts/validate_data.py
```

## Verification

```bash
cd frontend
npm run typecheck
npm run build
```

See [docs/architecture.md](docs/architecture.md), [docs/frontend-data.md](docs/frontend-data.md), [docs/analytics.md](docs/analytics.md), [docs/signals.md](docs/signals.md), [docs/implementation-roadmap.md](docs/implementation-roadmap.md), and [TODO.md](TODO.md).

## License and data

Code is licensed under Apache-2.0. Synthetic demo data is included only to make the application runnable after cloning; it must not be treated as market research. Future source data must retain provenance, attribution, and its applicable license.
