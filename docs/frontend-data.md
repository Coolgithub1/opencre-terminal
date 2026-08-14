# Static frontend data access

The terminal is served from GitHub Pages with no application server. Each pipeline run writes canonical data into `data/` and copies the complete versioned output into `frontend/public/data/v1/` before Vite builds the site. The deployment workflow repeats this step in GitHub Actions, so Pages always publishes the generated static data alongside the frontend.

The browser data layer in `frontend/src/data/client.ts` is the only frontend path to datasets. It resolves URLs through Vite's base path, which works both in local development and at the GitHub Pages repository subpath. Requests use browser revalidation, so a visitor receives a current generated dataset after a Pages deployment while still allowing HTTP caching when the file is unchanged.

## Loading strategy

- The dashboard loads only compact current signal rankings, current signals, recent events, five current synthetic economic indicators, and pipeline health.
- Markets loads the 20-record current analytics dataset.
- Signals loads 20 current scores first, then fetches exactly one 50-record file from `signals/history/{market_id}.json` after a market is selected.
- Events lazily loads the 20-record `events/extracted.json` rule output and matching 20-record `events/articles.json` feed metadata only when its page is opened.
- Historical Parquet files remain published for pipeline and future analytical use, but the browser does not download them for its interactive chart.

This preserves the static-first design while avoiding a startup download of all historical observations.

## Economic data boundary

The dashboard's `economic/latest.json` is a five-record deterministic synthetic baseline; the matching 250-record Parquet history remains browser-unloaded. BLS, Census, FRED, and SEC retrieval never runs in the browser and does not affect this bundle. When configured, those connectors execute only in a separate GitHub Actions workflow and retain their normalized results as a short-lived artifact.

## Map loading

The Map page lazily loads `geography/markets.geojson`, a 20-feature static collection, with the current signals and current market analytics. It performs the join and asset-class filter in the browser. MapLibre draws an empty terminal basemap and local point layers, so opening the map does not contact a tile service or mapping API.
