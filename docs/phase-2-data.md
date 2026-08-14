# Phase 2 data foundation

Run the deterministic dataset pipeline locally:

```bash
python -m pip install -r requirements.txt
python scripts/run_pipeline.py
python scripts/validate_data.py
```

`DuckDB` is used only in memory to write and inspect Parquet. The pipeline never starts a service or retains a database file. `Polars`, `NumPy`, `PyArrow`, and DuckDB provide the dataframe, deterministic numeric generation, interchange, and static-output layers.

## Generated files

- `data/markets/markets.json` — 20 synthetic markets.
- `data/markets/market_metrics.parquet` — 1,000 synthetic monthly market snapshots.
- `data/demo/properties.parquet` and `data/demo/hotels.parquet` — 100 properties and 50 hotels.
- `data/transactions/transactions.parquet` — 500 transactions.
- `data/events/history.parquet` and `data/events/latest.json` — 1,000 event records plus a compact current view.
- `data/index.json` — versioned file catalogue with path, timestamp, count, and schema version.
- `data/metadata/` — sources, update timestamp, validation report, and pipeline health.

Phase 3 derives static analytics and rankings from the market and event history; see [analytics.md](analytics.md). Phase 5 publishes the versioned generated data bundle to GitHub Pages and provides interactive analytics views without introducing a server dependency; see [frontend-data.md](frontend-data.md).
