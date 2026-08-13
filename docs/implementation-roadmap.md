# Implementation roadmap

The project is delivered in deliberately bounded phases to keep its static-first architecture verifiable.

1. **Foundation:** Vite React TypeScript frontend, GitHub Pages, terminal UI, synthetic demo data.
2. **Data foundation (complete):** Python 3.12-compatible pipelines, schemas, in-memory DuckDB/Parquet processing, generated demo datasets, validation, and CI.
3. **Market analytics (complete):** historical-percentile normalization, auditable market-state metrics, and static rankings.
4. **Signals (complete):** versioned weighted scores, validation, history, classifications, rankings, and mathematical explanations.
5. **Terminal analytics:** charts, tables, filtering, lazy data loading.
6. **Geography:** static GeoJSON, MapLibre layers, market detail panels.
7. **News events:** configurable RSS registry, deterministic event extraction, entity and geography resolution.
8. **Public economics:** credential-aware BLS, Census, FRED, and SEC connectors.
9. **Backtesting:** deterministic historical-association analysis.
10. **Hotel ingest:** browser-only workbook parsing, mapping, and validation.
11. **Hotel valuation:** cap-rate, price-per-key, and DCF models.
12. **Hotel comps and scenarios:** static comps, immediate client-side sensitivity calculations.
13. **Auditability:** alerts, data-quality reporting, methodology, data provenance, and project hardening.

Each phase must run its tests, linting, type checks, production build, relevant pipeline, and generated-data verification before the next phase begins.
