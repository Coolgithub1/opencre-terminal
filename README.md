# OpenCRE Terminal

OpenCRE Terminal is an open-source, static-first commercial real estate intelligence terminal. It is designed to run entirely through GitHub Pages and GitHub Actions, without a server, database, paid AI service, or proprietary data dependency.

## Current status

Phases 1 through 9 are complete. The project includes a Vite + React + TypeScript terminal shell, GitHub Pages deployment, reproducible static datasets, deterministic market analytics/rankings, configurable signals with complete score decompositions, interactive terminal charts/tables, a MapLibre market-signal map, rule-based RSS event extraction, credential-aware public economic connectors, and static historical-association backtesting. All displayed terminal values are explicitly labeled **DEMO DATA — synthetic, not real market data**. Map points are representative city centroids, not market or administrative boundaries.

## Phase 6: static geography

Phase 6 adds an on-demand MapLibre signal view backed by a versioned 20-feature GeoJSON collection. These are representative city-centroid points for synthetic demo markets, not market, MSA, property, or administrative boundaries. The terminal map uses an empty local style and no map tiles, token, mapping API, spatial database, or application server.

## Phase 7: RSS events

Phase 7 adds a configurable publisher RSS registry, metadata-only parser, deterministic URL deduplication, conservative entity and market resolution, and transparent event rules. The terminal publishes a synthetic fixture so builds remain reproducible. The scheduled workflow separately fetches the configured public feed registry into a short-lived Actions artifact; it never fetches article pages, republishes full article text, or exposes secrets.

## Phase 8: public economic connectors

The dashboard now includes a deterministic five-series United States economic baseline, generated with the same fixed seed and explicitly labeled as synthetic. A separate daily, read-only workflow can retrieve narrow BLS, Census, FRED, and SEC records only when the required GitHub Actions secrets are configured. It keeps live records in a seven-day artifact rather than deploying them to Pages, skips absent credentials without making a request, and never exposes credentials to the browser. See [docs/economic.md](docs/economic.md) for the reviewed endpoints, activation requirements, and source-governance policy.

## Phase 9: deterministic backtesting

The new Backtesting view filters a precomputed grid of synthetic signal-threshold observations by market or asset-class scope, threshold, and 3-, 6-, or 12-month forward horizon. It reports sample size, mean, median, standard deviation, percentile, and hit rate as historical associations only — never causation, prediction, or investment advice. See [docs/backtesting.md](docs/backtesting.md).

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

See [docs/architecture.md](docs/architecture.md), [docs/frontend-data.md](docs/frontend-data.md), [docs/analytics.md](docs/analytics.md), [docs/signals.md](docs/signals.md), [docs/geography.md](docs/geography.md), [docs/rss.md](docs/rss.md), [docs/economic.md](docs/economic.md), [docs/backtesting.md](docs/backtesting.md), [docs/implementation-roadmap.md](docs/implementation-roadmap.md), and [TODO.md](TODO.md).

## License and data

Code is licensed under Apache-2.0. Synthetic demo data is included only to make the application runnable after cloning; it must not be treated as market research. Future source data must retain provenance, attribution, and its applicable license.
