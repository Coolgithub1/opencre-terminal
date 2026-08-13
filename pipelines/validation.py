"""Read and validate generated static datasets independently of the generator."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import duckdb

from pipelines.schemas import DATASET_SPECS, PROVENANCE_COLUMNS


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

    return {"status": "healthy", "datasets": records}
