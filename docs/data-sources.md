# Data sources and provenance

## Phase 2: synthetic demo data only

## Phase 6: synthetic market geography

`data/geography/markets.geojson` is a generated 20-feature GeoJSON collection of representative city-centroid points. It is derived solely from the synthetic market registry, carries source, methodology, retrieval, and demo-label fields, and is copied unchanged into the GitHub Pages bundle. It is not a public boundary dataset and does not describe the extent of a real market, MSA, submarket, property, county, ZIP code, or census geography.

Every data file generated in Phase 2 is synthetic and carries the label `DEMO DATA — synthetic, deterministic, and not real market data.` No public-source connector has been activated, and no proprietary data is included.

The foundational records are produced by `pipelines/demo/generator.py` from a fixed seed (`20260813`). This makes the generated 20 markets, 100 properties, 50 hotels, 500 transactions, 1,000 market observations, and 1,000 events reproducible. Phase 3's analytics and rankings are derived only from these records through documented mathematical transformations. Their source fields identify either the OpenCRE synthetic generator or the deterministic analytics process, and `data/metadata/sources.json` records the licensing and update information.

## Phase 7: RSS metadata and rule-based events

The terminal uses 20 synthetic RSS fixture records in `data/events/articles.json` and 20 corresponding records in `data/events/extracted.json`. The fixture is clearly labeled demo data and exists to make the parser, deduplicator, entity resolver, market resolver, and event browser usable immediately after cloning. It is not reporting and is not real event data.

The separately scheduled public RSS workflow reads Federal Reserve Board press-release metadata from the reviewed registry. Its endpoint and usage guidance are recorded in `pipelines/rss/feeds.json`, and the Federal Reserve publishes its available feeds at `https://www.federalreserve.gov/feeds/feeds.htm`. The workflow retains only titles, URLs, dates, and feed summaries in a short-lived artifact, preserves publisher attribution, and never fetches article bodies. It does not alter the GitHub Pages demo dataset.

## Phase 8: synthetic economic baseline and optional public connectors

`data/economic/latest.json` contains five current illustrative United States economic indicators, and `data/economic/history.parquet` contains their 50-month synthetic histories. Like every other terminal dataset, these records are deterministic synthetic demo data; they are not observations copied or derived from a public agency. Each carries complete provenance pointing to the generation methodology.

The reviewed BLS, Census, FRED, and SEC connectors are intentionally separate from Pages. The daily read-only workflow writes live, normalized records only to a seven-day Actions artifact when the matching GitHub Actions credentials are available. It skips unavailable credentials without a network call, writes no secrets or credential-bearing request URLs to the artifact, and cannot modify the static terminal. Detailed activation, attribution, and source-governance requirements are in [economic.md](economic.md).

## Phase 9: synthetic historical association

`data/backtesting/results.json` contains derived descriptive summaries of the synthetic signal and market-metrics histories. Its source is the deterministic historical-association engine, its rows retain standard provenance fields, and it contains no public or proprietary market observations. The calculations and non-causal boundary are documented in [backtesting.md](backtesting.md).
