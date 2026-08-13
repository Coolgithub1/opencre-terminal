"""Calculate static market signals and their exact weighted decompositions."""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any

import polars as pl

from pipelines.demo.generator import DEMO_LABEL
from pipelines.signals.config import SignalDefinition, validate_signal_definitions

SIGNAL_SOURCE = "OpenCRE deterministic market signal engine"
SIGNAL_SOURCE_URL = "https://github.com/Coolgithub1/opencre-terminal/tree/main/docs/signals.md"
SIGNAL_METHODOLOGY = (
    "The signal is the sum of component score multiplied by explicit component weight. "
    "Each component is a 0–100 historical-percentile metric generated from synthetic data. "
    "Scores describe historical associations only and do not claim causation or predict "
    "performance."
)


def classify_score(score: float) -> str:
    """Assign one non-overlapping institutional label to a bounded score."""
    if score < 30:
        return "Weak"
    if score < 50:
        return "Neutral"
    if score < 70:
        return "Emerging"
    if score < 85:
        return "Strong"
    return "Exceptional"


def _definitions_by_asset_class(
    definitions: tuple[SignalDefinition, ...],
) -> dict[str, SignalDefinition]:
    validate_signal_definitions(definitions)
    return {definition.asset_class: definition for definition in definitions}


def _components(row: dict[str, Any], definition: SignalDefinition) -> list[dict[str, object]]:
    components: list[dict[str, object]] = []
    for component in definition.components:
        score = float(row[component.source_field])
        if not 0 <= score <= 100:
            raise ValueError(
                f"{definition.name}: {component.source_field} must be within 0–100, "
                f"received {score}"
            )
        contribution = score * component.weight / 100
        components.append(
            {
                "key": component.key,
                "label": component.label,
                "source_field": component.source_field,
                "score": round(score, 4),
                "weight": component.weight,
                "contribution": round(contribution, 4),
            }
        )
    return components


def calculate_signal_record(row: dict[str, Any], definition: SignalDefinition) -> dict[str, object]:
    """Calculate one signal with all source values and contribution arithmetic exposed."""
    components = _components(row, definition)
    score = round(sum(float(component["contribution"]) for component in components), 4)
    return {
        "signal_id": f"{row['market_id']}:{definition.key}:{row['observation_date']}",
        "signal_key": definition.key,
        "signal_name": definition.name,
        "signal_version": definition.version,
        "market_id": row["market_id"],
        "market_name": row["market_name"],
        "asset_class": row["asset_class"],
        "score": score,
        "classification": classify_score(score),
        "components": components,
        **{f"{component['key']}_score": component["score"] for component in components},
        **{
            f"{component['key']}_contribution": component["contribution"]
            for component in components
        },
        "source": SIGNAL_SOURCE,
        "source_url": SIGNAL_SOURCE_URL,
        "retrieved_at": row["retrieved_at"],
        "observation_date": row["observation_date"],
        "metric": "market_growth_signal",
        "value": score,
        "unit": "score",
        "geography": row["geography"],
        "methodology": SIGNAL_METHODOLOGY,
        "data_label": DEMO_LABEL,
    }


def build_signal_history(
    market_analytics: pl.DataFrame, definitions: tuple[SignalDefinition, ...]
) -> pl.DataFrame:
    """Calculate a static signal record per market analytics observation."""
    by_asset_class = _definitions_by_asset_class(definitions)
    records = []
    for row in market_analytics.sort(["market_id", "observation_date"]).to_dicts():
        try:
            definition = by_asset_class[row["asset_class"]]
        except KeyError as error:
            raise ValueError(
                f"No signal configuration for asset class {row['asset_class']}"
            ) from error
        record = calculate_signal_record(row, definition)
        record.pop("components")
        records.append(record)
    return pl.DataFrame(records).sort(["market_id", "observation_date"])


def latest_signal_records(
    signal_history: pl.DataFrame, definitions: tuple[SignalDefinition, ...]
) -> pl.DataFrame:
    """Attach explicit component arrays to one most-current signal per market."""
    by_key = {definition.key: definition for definition in definitions}
    latest_rows = (
        signal_history.sort(["market_id", "observation_date"])
        .group_by("market_id")
        .last()
        .sort("market_name")
        .to_dicts()
    )
    records = []
    for row in latest_rows:
        definition = by_key[row["signal_key"]]
        components = [
            {
                "key": component.key,
                "label": component.label,
                "source_field": component.source_field,
                "score": row[f"{component.key}_score"],
                "weight": component.weight,
                "contribution": row[f"{component.key}_contribution"],
            }
            for component in definition.components
        ]
        records.append({**row, "components": components})
    return pl.DataFrame(records)


def build_signal_rankings(latest_signals: pl.DataFrame) -> dict[str, object]:
    """Create compact static score leaderboards without discarding classifications."""
    rows = latest_signals.to_dicts()
    as_of_date = max(row["observation_date"] for row in rows)

    def ranked(descending: bool) -> list[dict[str, object]]:
        ordered = sorted(
            rows, key=lambda row: (row["score"], row["market_name"]), reverse=descending
        )
        return [
            {
                "rank": rank,
                "market_id": row["market_id"],
                "market_name": row["market_name"],
                "asset_class": row["asset_class"],
                "signal_name": row["signal_name"],
                "score": row["score"],
                "classification": row["classification"],
                "data_label": DEMO_LABEL,
            }
            for rank, row in enumerate(ordered[:10], start=1)
        ]

    return {
        "schema_version": "1.0.0",
        "data_label": DEMO_LABEL,
        "as_of_date": as_of_date,
        "source": SIGNAL_SOURCE,
        "source_url": SIGNAL_SOURCE_URL,
        "methodology": SIGNAL_METHODOLOGY,
        "rankings": {"top_signals": ranked(True), "bottom_signals": ranked(False)},
    }


def signal_explanations(latest_signals: Iterable[dict[str, object]]) -> list[dict[str, object]]:
    """Provide a deliberately compact data product for a future explanation panel."""
    return [
        {
            "signal_id": record["signal_id"],
            "market_name": record["market_name"],
            "signal_name": record["signal_name"],
            "score": record["score"],
            "classification": record["classification"],
            "components": record["components"],
            "data_label": DEMO_LABEL,
        }
        for record in latest_signals
    ]
