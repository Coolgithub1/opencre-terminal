"""Read and validate generated static datasets independently of the generator."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import duckdb

from pipelines.analytics.rankings import RANKING_DEFINITIONS
from pipelines.schemas import DATASET_SPECS, PROVENANCE_COLUMNS
from pipelines.signals.config import DEFAULT_SIGNAL_DEFINITIONS


class DataValidationError(ValueError):
    """Raised when an on-disk static dataset does not meet its contract."""


def _json_rows(path: Path) -> list[dict[str, Any]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, list) or not all(isinstance(row, dict) for row in payload):
        raise DataValidationError(f"{path}: expected a JSON array of objects")
    return payload


def validate_data_directory(data_dir: Path) -> dict[str, object]:
    """Validate dataset locations, record counts, schema fields, and provenance availability."""
    index_path = data_dir / "index.json"
    if not index_path.exists():
        raise DataValidationError(f"Missing dataset index: {index_path}")
    index = json.loads(index_path.read_text(encoding="utf-8"))
    if index.get("schema_version") != "1.0.0":
        raise DataValidationError("index.json must declare schema_version 1.0.0")
    indexed_paths = {entry["path"] for entry in index.get("datasets", [])}
    records: list[dict[str, object]] = []

    with duckdb.connect(":memory:") as connection:
        for spec in DATASET_SPECS:
            path = data_dir / spec.relative_path
            if not path.exists():
                raise DataValidationError(f"Missing {spec.name} dataset: {path}")
            if spec.relative_path.as_posix() not in indexed_paths:
                raise DataValidationError(f"{spec.name} is absent from data/index.json")
            if spec.storage == "json":
                rows = _json_rows(path)
                columns = set(rows[0]) if rows else set()
                row_count = len(rows)
                null_provenance = [
                    field
                    for field in PROVENANCE_COLUMNS
                    if any(row.get(field) in (None, "") for row in rows)
                ]
            else:
                safe_path = path.resolve().as_posix().replace("'", "''")
                row_count = connection.execute(
                    f"SELECT count(*) FROM read_parquet('{safe_path}')"
                ).fetchone()[0]
                columns = {
                    row[0]
                    for row in connection.execute(
                        f"DESCRIBE SELECT * FROM read_parquet('{safe_path}')"
                    ).fetchall()
                }
                null_provenance = [
                    field
                    for field in PROVENANCE_COLUMNS
                    if connection.execute(
                        "SELECT count(*) "
                        f"FROM read_parquet('{safe_path}') "
                        f'WHERE "{field}" IS NULL OR CAST("{field}" AS VARCHAR) = \'\''
                    ).fetchone()[0]
                    > 0
                ]
            missing_columns = sorted(spec.required_columns.difference(columns))
            if row_count != spec.expected_rows:
                raise DataValidationError(
                    f"{spec.name}: expected {spec.expected_rows} rows, received {row_count}"
                )
            if missing_columns:
                raise DataValidationError(f"{spec.name}: missing columns {missing_columns}")
            if null_provenance:
                raise DataValidationError(
                    f"{spec.name}: missing provenance values {null_provenance}"
                )
            records.append({"name": spec.name, "records": row_count, "status": "valid"})

    rankings_path = data_dir / "markets/rankings.json"
    if "markets/rankings.json" not in indexed_paths:
        raise DataValidationError("market rankings are absent from data/index.json")
    if not rankings_path.exists():
        raise DataValidationError(f"Missing market rankings dataset: {rankings_path}")
    rankings = json.loads(rankings_path.read_text(encoding="utf-8"))
    ranking_lists = rankings.get("rankings", {})
    for ranking_name in RANKING_DEFINITIONS:
        entries = ranking_lists.get(ranking_name)
        if not isinstance(entries, list) or len(entries) != 5:
            raise DataValidationError(f"{ranking_name}: expected five ranking entries")
        if [entry.get("rank") for entry in entries] != [1, 2, 3, 4, 5]:
            raise DataValidationError(f"{ranking_name}: ranks must be consecutive from one to five")
    records.append({"name": "market_rankings", "records": 40, "status": "valid"})

    signal_rankings_path = data_dir / "signals/rankings.json"
    signal_explanations_path = data_dir / "signals/explanations.json"
    signal_configs_path = data_dir / "metadata/signal_configs.json"
    expected_signal_paths = {
        "signals/rankings.json",
        "signals/explanations.json",
        "metadata/signal_configs.json",
    }
    if not expected_signal_paths.issubset(indexed_paths):
        raise DataValidationError("signal metadata is absent from data/index.json")
    if not signal_rankings_path.exists() or not signal_explanations_path.exists():
        raise DataValidationError("signal ranking or explanation output is missing")
    signal_rankings = json.loads(signal_rankings_path.read_text(encoding="utf-8"))
    for ranking_name in ("top_signals", "bottom_signals"):
        entries = signal_rankings.get("rankings", {}).get(ranking_name)
        if not isinstance(entries, list) or len(entries) != 10:
            raise DataValidationError(f"{ranking_name}: expected ten signal ranking entries")
        if [entry.get("rank") for entry in entries] != list(range(1, 11)):
            raise DataValidationError(f"{ranking_name}: ranks must be consecutive from one to ten")
    explanations = _json_rows(signal_explanations_path)
    if len(explanations) != 20 or any(len(row.get("components", [])) != 6 for row in explanations):
        raise DataValidationError("signal explanations must contain 20 six-component records")
    signal_configs = json.loads(signal_configs_path.read_text(encoding="utf-8"))
    if len(signal_configs.get("configurations", [])) != len(DEFAULT_SIGNAL_DEFINITIONS):
        raise DataValidationError(
            "signal configuration count does not match the registered definitions"
        )
    signal_history_directory = data_dir / "signals/history"
    history_files = sorted(signal_history_directory.glob("*.json"))
    if len(history_files) != 20:
        raise DataValidationError("expected one signal-history JSON file for each of 20 markets")
    if any(len(_json_rows(path)) != 50 for path in history_files):
        raise DataValidationError(
            "each market signal-history JSON file must contain 50 observations"
        )
    records.extend(
        [
            {"name": "signal_rankings", "records": 20, "status": "valid"},
            {"name": "signal_explanations", "records": 20, "status": "valid"},
            {
                "name": "signal_configurations",
                "records": len(DEFAULT_SIGNAL_DEFINITIONS),
                "status": "valid",
            },
            {"name": "signal_history_by_market", "records": 1_000, "status": "valid"},
        ]
    )

    geography_path = data_dir / "geography/markets.geojson"
    if "geography/markets.geojson" not in indexed_paths:
        raise DataValidationError("market geography is absent from data/index.json")
    if not geography_path.exists():
        raise DataValidationError("market geography output is missing")
    geography = json.loads(geography_path.read_text(encoding="utf-8"))
    features = geography.get("features", [])
    if geography.get("type") != "FeatureCollection" or len(features) != 20:
        raise DataValidationError("market geography must be a 20-feature GeoJSON collection")
    market_ids = {feature.get("properties", {}).get("market_id") for feature in features}
    if len(market_ids) != 20 or None in market_ids:
        raise DataValidationError("market geography must have one unique market_id per feature")
    for feature in features:
        coordinates = feature.get("geometry", {}).get("coordinates", [])
        if feature.get("geometry", {}).get("type") != "Point" or len(coordinates) != 2:
            raise DataValidationError("market geography features must be point geometries")
        longitude, latitude = coordinates
        if not (-180 <= longitude <= 180 and -90 <= latitude <= 90):
            raise DataValidationError(
                "market geography coordinates are outside valid geographic bounds"
            )
    records.append({"name": "market_geography", "records": 20, "status": "valid"})

    rss_articles_path = data_dir / "events/articles.json"
    extracted_events_path = data_dir / "events/extracted.json"
    expected_rss_paths = {"events/articles.json", "events/extracted.json"}
    if not expected_rss_paths.issubset(indexed_paths):
        raise DataValidationError("RSS outputs are absent from data/index.json")
    if not rss_articles_path.exists() or not extracted_events_path.exists():
        raise DataValidationError("RSS article or extracted-event output is missing")
    rss_articles = _json_rows(rss_articles_path)
    extracted_events = _json_rows(extracted_events_path)
    if len(rss_articles) != 20 or len(extracted_events) != 20:
        raise DataValidationError("expected 20 RSS articles and 20 extracted events")
    if len({article.get("url") for article in rss_articles}) != 20:
        raise DataValidationError("RSS article URLs must be unique after deduplication")
    article_ids = {article.get("article_id") for article in rss_articles}
    required_event_fields = {
        "event_id",
        "article_id",
        "event_type",
        "company",
        "market_id",
        "location",
        "event_date",
        "confidence",
        *PROVENANCE_COLUMNS,
    }
    for event in extracted_events:
        if not required_event_fields.issubset(event):
            raise DataValidationError("RSS extracted events are missing required fields")
        if event.get("article_id") not in article_ids:
            raise DataValidationError("RSS event references an unknown article")
        confidence = event.get("confidence")
        if not isinstance(confidence, (float, int)) or not 0 <= confidence <= 1:
            raise DataValidationError("RSS event confidence must be between zero and one")
    records.extend(
        [
            {"name": "rss_articles", "records": 20, "status": "valid"},
            {"name": "extracted_events", "records": 20, "status": "valid"},
        ]
    )

    return {"status": "healthy", "datasets": records}
