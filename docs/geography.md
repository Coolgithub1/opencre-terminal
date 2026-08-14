# Static market geography

Phase 6 publishes `data/geography/markets.geojson` and copies it to the versioned GitHub Pages bundle at `frontend/public/data/v1/geography/markets.geojson`. It is a 20-feature GeoJSON `FeatureCollection`, with one point per synthetic market.

## Meaning and limits

Each point is a representative city centroid chosen solely to demonstrate browser mapping for the corresponding synthetic market. It is not a legal market boundary, MSA boundary, submarket boundary, property location, county, ZIP code, census geography, or an assertion about a real market's extent. The generated fields preserve the synthetic data label, source, source URL, retrieval time, observation date, metric, unit, geography type, and methodology.

## Rendering

The browser loads this small static collection only when the Map page opens, joins it to the current static market signals and analytics in memory, and renders it with MapLibre. The terminal style has an intentionally empty background layer: it fetches no map tiles, requires no map token, calls no third-party mapping API, and uses no spatial database. Circle color and size communicate the current deterministic signal score; they are not a valuation, recommendation, or forecast.

## Validation

The pipeline checks that the GeoJSON is indexed, contains exactly 20 unique market identifiers, uses point geometries, and has valid longitude/latitude bounds. Unit and pipeline tests verify that its output is deterministic and is included in the browser bundle.
