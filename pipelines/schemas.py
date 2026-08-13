"""Schema contracts for Phase 2 generated datasets."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import polars as pl

PROVENANCE_COLUMNS = frozenset(
    {
        "source",
        "source_url",
        "retrieved_at",
        "observation_date",
        "metric",
        "value",
        "unit",
        "geography",
        "methodology",
        "data_label",
    }
)


@dataclass(frozen=True)
class DatasetSpec:
    """Static dataset contract used both by the pipeline and validator."""

    name: str
    relative_path: Path
    expected_rows: int
    required_columns: frozenset[str]
    storage: str


DATASET_SPECS = (
    DatasetSpec(
        "markets",
        Path("markets/markets.json"),
        20,
        frozenset({"market_id", "market_name", "state", "msa", *PROVENANCE_COLUMNS}),
        "json",
    ),
    DatasetSpec(
        "market_metrics",
        Path("markets/market_metrics.parquet"),
        1_000,
        frozenset(
            {
                "market_id",
                "employment_growth",
                "rent_growth",
                "vacancy_rate",
                "transaction_volume",
                *PROVENANCE_COLUMNS,
            }
        ),
        "parquet",
    ),
    DatasetSpec(
        "events",
        Path("events/history.parquet"),
        1_000,
        frozenset({"event_id", "event_type", "location", "event_date", *PROVENANCE_COLUMNS}),
        "parquet",
    ),
    DatasetSpec(
        "transactions",
        Path("transactions/transactions.parquet"),
        500,
        frozenset(
            {"transaction_id", "property_id", "sale_price", "transaction_date", *PROVENANCE_COLUMNS}
        ),
        "parquet",
    ),
    DatasetSpec(
        "properties",
        Path("demo/properties.parquet"),
        100,
        frozenset(
            {
                "property_id",
                "market_id",
                "property_type",
                "rentable_square_feet",
                *PROVENANCE_COLUMNS,
            }
        ),
        "parquet",
    ),
    DatasetSpec(
        "hotels",
        Path("demo/hotels.parquet"),
        50,
        frozenset({"hotel_id", "market_id", "rooms", "adr", "occupancy", *PROVENANCE_COLUMNS}),
        "parquet",
    ),
)


class SchemaValidationError(ValueError):
    """Raised when generated records do not satisfy a public dataset contract."""


def validate_frame(frame: pl.DataFrame, spec: DatasetSpec) -> None:
    """Validate row count, required fields, provenance, and missing values before output."""
    missing_columns = spec.required_columns.difference(frame.columns)
    if missing_columns:
        raise SchemaValidationError(f"{spec.name}: missing columns {sorted(missing_columns)}")
    if frame.height != spec.expected_rows:
        raise SchemaValidationError(
            f"{spec.name}: expected {spec.expected_rows} rows, received {frame.height}"
        )
    empty_provenance = frame.select(
        [pl.col(column).is_null().any().alias(column) for column in PROVENANCE_COLUMNS]
    ).row(0, named=True)
    absent = sorted(column for column, has_null in empty_provenance.items() if has_null)
    if absent:
        raise SchemaValidationError(f"{spec.name}: null provenance fields {absent}")
