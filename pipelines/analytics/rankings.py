"""Create deterministic and transparent market-rankings data products."""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any

import polars as pl

from pipelines.analytics.market_state import (
    ANALYTICS_METHODOLOGY,
    ANALYTICS_SOURCE,
    ANALYTICS_SOURCE_URL,
    NORMALIZATION_METHOD,
)
from pipelines.demo.generator import DEMO_LABEL

RANKING_DEFINITIONS = {
    "top_markets": ("market_activity_score", True),
    "bottom_markets": ("market_activity_score", False),
    "fastest_improving": ("six_month_change", True),
    "fastest_deteriorating": ("six_month_change", False),
    "strongest_demand": ("demand_score", True),
    "weakest_supply": ("supply_balance_score", False),
    "highest_rent_momentum": ("rent_growth_percentile", True),
    "highest_investment_activity": ("capital_activity_score", True),
}


def _rank_rows(
    rows: Iterable[dict[str, Any]], field: str, descending: bool
) -> list[dict[str, Any]]:
    ordered = sorted(
        rows, key=lambda row: (float(row[field]), row["market_name"]), reverse=descending
    )
    return [
        {
            "rank": rank,
            "market_id": row["market_id"],
            "market_name": row["market_name"],
            "asset_class": row["asset_class"],
            "ranking_metric": field,
            "score": round(float(row[field]), 4),
            "market_activity_score": row["market_activity_score"],
            "six_month_change": row["six_month_change"],
            "data_label": DEMO_LABEL,
        }
        for rank, row in enumerate(ordered[:5], start=1)
    ]


def build_rankings(latest: pl.DataFrame) -> dict[str, object]:
    """Build ranking lists from current analytics without hiding score definitions."""
    rows = latest.to_dicts()
    as_of_date = max(row["observation_date"] for row in rows)
    return {
        "schema_version": "1.0.0",
        "data_label": DEMO_LABEL,
        "as_of_date": as_of_date,
        "normalization_method": NORMALIZATION_METHOD,
        "source": ANALYTICS_SOURCE,
        "source_url": ANALYTICS_SOURCE_URL,
        "methodology": ANALYTICS_METHODOLOGY,
        "rankings": {
            name: _rank_rows(rows, field, descending)
            for name, (field, descending) in RANKING_DEFINITIONS.items()
        },
    }
