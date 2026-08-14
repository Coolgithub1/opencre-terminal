"""Build auditable, non-causal backtest summaries from the synthetic time series."""

from __future__ import annotations

from statistics import mean, median, pstdev
from typing import Any

import numpy as np
import polars as pl

from pipelines.demo.generator import DEMO_LABEL

BACKTEST_SOURCE = "OpenCRE deterministic historical-association engine"
BACKTEST_SOURCE_URL = (
    "https://github.com/Coolgithub1/opencre-terminal/blob/main/docs/backtesting.md"
)
BACKTEST_METHODOLOGY = (
    "For each signal observation, the engine compares the score with the same synthetic market's "
    "rent-growth value three, six, or twelve months later. Summaries are descriptive historical "
    "associations only: they do not claim causation or predict future performance. Hit rate "
    "is the share of selected observations above the all-market median forward outcome at the same "
    "horizon."
)
THRESHOLDS = (50, 60, 70)
FORWARD_HORIZONS = (3, 6, 12)


def _scopes(signal_rows: list[dict[str, Any]]) -> list[dict[str, str]]:
    """Create stable all-market, asset-class, and individual-market selection scopes."""
    scopes = [
        {
            "scope_id": "all-markets",
            "scope_type": "universe",
            "scope_name": "All synthetic markets",
            "market_id": "",
            "asset_class": "All",
        }
    ]
    asset_classes = sorted({str(row["asset_class"]) for row in signal_rows})
    scopes.extend(
        {
            "scope_id": f"asset:{asset_class.casefold()}",
            "scope_type": "asset_class",
            "scope_name": f"{asset_class} markets",
            "market_id": "",
            "asset_class": asset_class,
        }
        for asset_class in asset_classes
    )
    market_rows = {
        str(row["market_id"]): (str(row["market_name"]), str(row["asset_class"]))
        for row in signal_rows
    }
    scopes.extend(
        {
            "scope_id": f"market:{market_id}",
            "scope_type": "market",
            "scope_name": market_name,
            "market_id": market_id,
            "asset_class": asset_class,
        }
        for market_id, (market_name, asset_class) in sorted(market_rows.items())
    )
    return scopes


def _forward_observations(
    signal_history: pl.DataFrame, market_metrics: pl.DataFrame, horizon: int
) -> list[dict[str, object]]:
    """Join each signal to a later same-market rent-growth observation without look-ahead."""
    metrics_by_market = {
        market_id[0]: rows.sort("observation_date").to_dicts()
        for market_id, rows in market_metrics.group_by("market_id", maintain_order=True)
    }
    outcomes = {
        (str(row["market_id"]), str(row["observation_date"])): float(row["rent_growth"])
        for rows in metrics_by_market.values()
        for row in rows
    }
    observations: list[dict[str, object]] = []
    for market_id, rows in signal_history.group_by("market_id", maintain_order=True):
        ordered = rows.sort("observation_date").to_dicts()
        for index, signal in enumerate(ordered[:-horizon]):
            future_date = str(ordered[index + horizon]["observation_date"])
            observations.append(
                {
                    "market_id": str(market_id[0]),
                    "market_name": str(signal["market_name"]),
                    "asset_class": str(signal["asset_class"]),
                    "observation_date": str(signal["observation_date"]),
                    "forward_observation_date": future_date,
                    "score": float(signal["score"]),
                    "outcome": outcomes[(str(market_id[0]), future_date)],
                }
            )
    return observations


def _in_scope(observation: dict[str, object], scope: dict[str, str]) -> bool:
    if scope["scope_type"] == "universe":
        return True
    if scope["scope_type"] == "market":
        return observation["market_id"] == scope["market_id"]
    return observation["asset_class"] == scope["asset_class"]


def build_backtest_results(
    signal_history: pl.DataFrame,
    market_metrics: pl.DataFrame,
) -> list[dict[str, object]]:
    """Return a fixed grid of static backtest summaries for browser-side selection."""
    signal_rows = signal_history.to_dicts()
    scopes = _scopes(signal_rows)
    results: list[dict[str, object]] = []
    for horizon in FORWARD_HORIZONS:
        observations = _forward_observations(signal_history, market_metrics, horizon)
        reference_outcomes = [float(observation["outcome"]) for observation in observations]
        reference_median = median(reference_outcomes)
        for scope in scopes:
            scoped = [observation for observation in observations if _in_scope(observation, scope)]
            for threshold in THRESHOLDS:
                selected = [
                    observation
                    for observation in scoped
                    if float(observation["score"]) >= threshold
                ]
                selected_outcomes = [float(observation["outcome"]) for observation in selected]
                sample_size = len(selected_outcomes)
                mean_outcome = mean(selected_outcomes) if selected_outcomes else 0.0
                percentile = (
                    float(np.mean(np.asarray(reference_outcomes) <= mean_outcome) * 100)
                    if selected_outcomes
                    else 0.0
                )
                results.append(
                    {
                        "result_id": f"{scope['scope_id']}:{threshold}:{horizon}",
                        **scope,
                        "strategy": "signal_threshold",
                        "threshold": threshold,
                        "forward_horizon_months": horizon,
                        "historical_start": min(str(item["observation_date"]) for item in scoped),
                        "historical_end": max(str(item["observation_date"]) for item in scoped),
                        "sample_size": sample_size,
                        "mean_outcome": round(mean_outcome, 4),
                        "median_outcome": (
                            round(median(selected_outcomes), 4) if selected_outcomes else 0.0
                        ),
                        "standard_deviation": round(pstdev(selected_outcomes), 4)
                        if sample_size > 1
                        else 0.0,
                        "outcome_percentile": round(percentile, 2),
                        "hit_rate": round(
                            100
                            * sum(value > reference_median for value in selected_outcomes)
                            / sample_size,
                            2,
                        )
                        if sample_size
                        else 0.0,
                        "average_signal_score": (
                            round(mean(float(item["score"]) for item in selected), 2)
                            if selected
                            else 0.0
                        ),
                        "source": BACKTEST_SOURCE,
                        "source_url": BACKTEST_SOURCE_URL,
                        "retrieved_at": str(signal_rows[0]["retrieved_at"]),
                        "observation_date": max(str(item["observation_date"]) for item in scoped),
                        "metric": "forward_rent_growth",
                        "value": round(mean_outcome, 4),
                        "unit": "percent",
                        "geography": scope["scope_name"],
                        "methodology": BACKTEST_METHODOLOGY,
                        "data_label": DEMO_LABEL,
                    }
                )
    return sorted(results, key=lambda result: str(result["result_id"]))
