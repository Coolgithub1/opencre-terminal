# OpenCRE Terminal implementation roadmap

## Phase 1 — Static terminal foundation (complete)

- [x] Create a Vite, React, TypeScript, and Tailwind CSS frontend.
- [x] Build a dark, institutional terminal dashboard using synthetic demo data.
- [x] Add a small versioned static dataset and a centralized browser data layer.
- [x] Add GitHub Pages deployment workflow.
- [x] Add architecture and implementation documentation.
- [x] Verify type checking and production build.

## Phase 2 — Data foundation (complete)

- [x] Define versioned static-data contracts with required provenance fields.
- [x] Add a deterministic synthetic-data generator using Polars and NumPy.
- [x] Generate JSON and DuckDB-written Parquet files without a database server.
- [x] Add dataset validation, pipeline health metadata, Pytest coverage, and GitHub Actions validation.
- [x] Document the synthetic-data source and local pipeline.

## Phase 3 — Market analytics and rankings (complete)

- [x] Add historical-percentile, min–max, and z-score normalization utilities.
- [x] Generate audited demand, supply, performance, capital, event, and market-activity analytics.
- [x] Generate top/bottom, momentum, demand, supply, rent, and investment rankings.
- [x] Validate analytics/ranking outputs and document their methodology.

## Phase 4 — Configurable signals (complete)

- [x] Add versioned asset-class signal configurations with exact weight validation.
- [x] Generate signal history, latest scores, classifications, rankings, and explanations.
- [x] Expose every score's component values, weights, and weighted contributions.
- [x] Add golden decomposition tests and audit documentation.

## Phase 5 — Interactive terminal (complete)

- [x] Publish generated data into the versioned GitHub Pages frontend bundle.
- [x] Replace hardcoded dashboard data with centralized static dataset access.
- [x] Add interactive dashboard, market table, signal filters, score decomposition, and lazy history chart.
- [x] Add data-source catalogue and verify the browser loading strategy.

## Phase 6 - MapLibre and static geographic datasets (complete)

- [x] Generate and validate a provenance-carrying market-centroid GeoJSON collection.
- [x] Publish GeoJSON in the versioned static frontend bundle.
- [x] Add browser-only MapLibre signal points, asset-class filtering, market details, and a signal handoff.
- [x] Document that the geometry is representative city-centroid points, not boundaries.

## Phase 7 - RSS ingestion and deterministic event extraction (complete)

- [x] Add a reviewed RSS registry, metadata-only parser, URL deduplication, and scheduled Action artifact.
- [x] Generate 20 deterministic synthetic feed records and matching market-associated events for the static bundle.
- [x] Add exact and conservative fuzzy entity resolution, transparent event phrases, confidence, and provenance.
- [x] Add a terminal Events view with filters, source links, and extraction detail.

## Deferred phases

- [ ] Phase 8: public economic-data connectors.
- [ ] Phase 9: deterministic backtesting.
- [ ] Phase 10: client-side hotel spreadsheet parsing and validation.
- [ ] Phase 11: hotel valuation and DCF.
- [ ] Phase 12: hotel comparables and scenarios.
- [ ] Phase 13: alerts, data-quality reporting, methodology, and project hardening.
