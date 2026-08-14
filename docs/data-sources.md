# Data sources and provenance

## Phase 2: synthetic demo data only

## Phase 6: synthetic market geography

`data/geography/markets.geojson` is a generated 20-feature GeoJSON collection of representative city-centroid points. It is derived solely from the synthetic market registry, carries source, methodology, retrieval, and demo-label fields, and is copied unchanged into the GitHub Pages bundle. It is not a public boundary dataset and does not describe the extent of a real market, MSA, submarket, property, county, ZIP code, or census geography.

Every data file generated in Phase 2 is synthetic and carries the label `DEMO DATA — synthetic, deterministic, and not real market data.` No public-source connector has been activated, and no proprietary data is included.

The foundational records are produced by `pipelines/demo/generator.py` from a fixed seed (`20260813`). This makes the generated 20 markets, 100 properties, 50 hotels, 500 transactions, 1,000 market observations, and 1,000 events reproducible. Phase 3's analytics and rankings are derived only from these records through documented mathematical transformations. Their source fields identify either the OpenCRE synthetic generator or the deterministic analytics process, and `data/metadata/sources.json` records the licensing and update information.

Public BLS, Census, FRED, SEC, and RSS connectors remain later phases. They will only be added with documented licenses, terms, attribution, retrieval timestamps, and transformations. No connector may expose secrets to the browser.
