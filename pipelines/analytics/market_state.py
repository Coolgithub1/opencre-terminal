"""Calculate reproducible market-state analytics from market, event, and transaction facts."""

from __future__ import annotations

from collections import Counter, defaultdict
from datetime import date
from typing import Any

import polars as pl

from pipelines.analytics.normalization import normalize
from pipelines.demo.generator import DEMO_LABEL

NORMALIZATION_METHOD = "historical_percentile"
ANALYTICS_SOURCE = "OpenCRE deterministic market analytics"
ANALYTICS_SOURCE_URL = "https://github.com/Coolgithub1/opencre-terminal/tree/main/docs/analytics.md"
ANALYTICS_METHODOLOGY = (
    "Historical-percentile normalization within each synthetic market. Demand combines employment "
    "and population growth; supply balance inverses vacancy and construction pipeline; performance "
    "combines rent growth and absorption; capital activity reflects transaction volume; "
    "event activity reflects monthly synthetic event counts. Market activity is a weighted "
    "descriptive index, not an "
    "investment recommendation or causal claim."
)


def _month_start(value: str) -> str:
    parsed = date.fromisoformat(value)
    return parsed.replace(day=1).isoformat()


def _event_counts(events: pl.DataFrame) -> Counter[tuple[str, str]]:
    return Counter((row["market_id"], _month_start(row["event_date"])) for row in events.to_dicts())


def _percentiles(rows: list[dict[str, Any]], field: str, invert: bool = False) -> list[float]:
    values = normalize([float(row[field]) for row in rows], NORMALIZATION_METHOD)
    return [round(100 - value if invert else value, 4) for value in values]


def build_market_analytics(metrics: pl.DataFrame, events: pl.DataFrame) -> pl.DataFrame:
    """Calculate auditable historical market analytics for every metric snapshot."""
    event_counts = _event_counts(events)
    by_market: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in metrics.sort(["market_id", "observation_date"]).to_dicts():
        row["event_count"] = event_counts[(row["market_id"], row["observation_date"])]
        by_market[row["market_id"]].append(row)

    analytics_rows: list[dict[str, Any]] = []
    for rows in by_market.values():
        normalized = {
            "employment_growth_percentile": _percentiles(rows, "employment_growth"),
            "population_growth_percentile": _percentiles(rows, "population_growth"),
            "rent_growth_percentile": _percentiles(rows, "rent_growth"),
            "vacancy_percentile_inverse": _percentiles(rows, "vacancy_rate", invert=True),
            "absorption_percentile": _percentiles(rows, "absorption"),
            "construction_percentile_inverse": _percentiles(
                rows, "construction_pipeline", invert=True
            ),
            "capital_activity_score": _percentiles(rows, "transaction_volume"),
            "event_activity_score": _percentiles(rows, "event_count"),
        }
        activity_history: list[float] = []
        for index, row in enumerate(rows):
            demand_score = (
                normalized["employment_growth_percentile"][index] * 0.6
                + normalized["population_growth_percentile"][index] * 0.4
            )
            supply_balance_score = (
                normalized["vacancy_percentile_inverse"][index] * 0.65
                + normalized["construction_percentile_inverse"][index] * 0.35
            )
            performance_score = (
                normalized["rent_growth_percentile"][index] * 0.6
                + normalized["absorption_percentile"][index] * 0.4
            )
            market_activity_score = (
                demand_score * 0.25
                + supply_balance_score * 0.15
                + performance_score * 0.3
                + normalized["capital_activity_score"][index] * 0.2
                + normalized["event_activity_score"][index] * 0.1
            )
            activity_history.append(market_activity_score)
            prior_index = max(0, index - 6)
            six_month_change = market_activity_score - activity_history[prior_index]
            analytics_rows.append(
                {
                    "market_id": row["market_id"],
                    "market_name": row["market_name"],
                    "asset_class": row["asset_class"],
                    "employment_growth": row["employment_growth"],
                    "population_growth": row["population_growth"],
                    "rent_growth": row["rent_growth"],
                    "vacancy_rate": row["vacancy_rate"],
                    "absorption": row["absorption"],
                    "transaction_volume": row["transaction_volume"],
                    "construction_pipeline": row["construction_pipeline"],
                    "event_count": row["event_count"],
                    **{name: values[index] for name, values in normalized.items()},
                    "demand_score": round(demand_score, 4),
                    "supply_balance_score": round(supply_balance_score, 4),
                    "performance_score": round(performance_score, 4),
                    "market_activity_score": round(market_activity_score, 4),
                    "six_month_change": round(six_month_change, 4),
                    "normalization_method": NORMALIZATION_METHOD,
                    "source": ANALYTICS_SOURCE,
                    "source_url": ANALYTICS_SOURCE_URL,
                    "retrieved_at": row["retrieved_at"],
                    "observation_date": row["observation_date"],
                    "metric": "market_activity_score",
                    "value": round(market_activity_score, 4),
                    "unit": "score",
                    "geography": row["geography"],
                    "methodology": ANALYTICS_METHODOLOGY,
                    "data_label": DEMO_LABEL,
                }
            )
    return pl.DataFrame(analytics_rows).sort(["market_id", "observation_date"])


def latest_market_analytics(history: pl.DataFrame) -> pl.DataFrame:
    """Return exactly one current analytics record per market."""
    return (
        history.sort(["market_id", "observation_date"])
        .group_by("market_id")
        .last()
        .sort("market_name")
    )
