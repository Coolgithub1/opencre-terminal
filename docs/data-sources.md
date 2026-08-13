# Data sources and provenance

## Phase 2: synthetic demo data only

Every data file generated in Phase 2 is synthetic and carries the label `DEMO DATA — synthetic, deterministic, and not real market data.` No public-source connector has been activated, and no proprietary data is included.

The records are produced by `pipelines/demo/generator.py` from a fixed seed (`20260813`). This makes the generated 20 markets, 100 properties, 50 hotels, 500 transactions, 1,000 market observations, and 1,000 events reproducible. Their source fields identify the OpenCRE synthetic generator, their methodology states that they are not market observations, and `data/metadata/sources.json` records the licensing and update information.

Public BLS, Census, FRED, SEC, and RSS connectors remain later phases. They will only be added with documented licenses, terms, attribution, retrieval timestamps, and transformations. No connector may expose secrets to the browser.
