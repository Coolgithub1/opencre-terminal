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

## Deferred phases

- [ ] Phase 4: configurable signal engine and audit-ready decompositions.
- [ ] Phase 5: interactive terminal charts and tables.
- [ ] Phase 6: MapLibre and static geographic datasets.
- [ ] Phase 7: RSS ingestion and deterministic event extraction.
- [ ] Phase 8: public economic-data connectors.
- [ ] Phase 9: deterministic backtesting.
- [ ] Phase 10: client-side hotel spreadsheet parsing and validation.
- [ ] Phase 11: hotel valuation and DCF.
- [ ] Phase 12: hotel comparables and scenarios.
- [ ] Phase 13: alerts, data-quality reporting, methodology, and project hardening.
