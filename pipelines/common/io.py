"""Safe writers for static, versioned project datasets."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import duckdb
import pyarrow as pa


def write_json(path: Path, payload: Any) -> None:
    """Write stable UTF-8 JSON, creating its parent directory when needed."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_parquet(path: Path, records: pa.Table) -> None:
    """Write Parquet through in-memory DuckDB; no database file is retained."""
    path.parent.mkdir(parents=True, exist_ok=True)
    escaped_path = path.resolve().as_posix().replace("'", "''")
    with duckdb.connect(":memory:") as connection:
        connection.register("dataset_rows", records)
        connection.execute(
            f"COPY dataset_rows TO '{escaped_path}' (FORMAT PARQUET, COMPRESSION ZSTD)"
        )
