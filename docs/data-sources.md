# Data sources and provenance

## Phase 2: synthetic demo data only

## Phase 6: synthetic market geography

`data/geography/markets.geojson` is a generated 20-feature GeoJSON collection of representative city-centroid points. It is derived solely from the synthetic market registry, carries source, methodology, retrieval, and demo-label fields, and is copied unchanged into the GitHub Pages bundle. It is not a public boundary dataset and does not describe the extent of a real market, MSA, submarket, property, county, ZIP code, or census geography.

Every data file generated in Phase 2 is synthetic and carries the label `DEMO DATA — synthetic, deterministic, and not real market data.` No public-source connector has been activated, and no proprietary data is included.

The foundational records are produced by `pipelines/demo/generator.py` from a fixed seed (`20260813`). This makes the generated 20 markets, 100 properties, 50 hotels, 500 transactions, 1,000 market observations, and 1,000 events reproducible. Phase 3's analytics and rankings are derived only from these records through documented mathematical transformations. Their source fields identify either the OpenCRE synthetic generator or the deterministic analytics process, and `data/metadata/sources.json` records the licensing and update information.

## Phase 7: RSS metadata and rule-based events

The terminal uses 20 synthetic RSS fixture records in `data/events/articles.json` and 20 corresponding records in `data/events/extracted.json`. The fixture is clearly labeled demo data and exists to make the parser, deduplicator, entity resolver, market resolver, and event browser usable immediately after cloning. It is not reporting and is not real event data.

The separately scheduled public RSS workflow reads Federal Reserve Board press-release metadata from the reviewed registry. Its endpoint and usage guidance are recorded in `pipelines/rss/feeds.json`, and the Federal Reserve publishes its available feeds at `https://www.federalreserve.gov/feeds/feeds.htm`. The workflow retains only titles, URLs, dates, and feed summaries in a short-lived artifact, preserves publisher attribution, and never fetches article bodies. It does not alter the GitHub Pages demo dataset.

Public Census, FRED, and SEC connectors remain later phases. They will only be added with documented licenses, terms, attribution, retrieval timestamps, and transformations. No connector may expose secrets to the browser.
