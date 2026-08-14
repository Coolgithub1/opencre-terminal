"""Generate a small, deterministic economic-indicator fixture for the static terminal."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date

import numpy as np
import polars as pl

from pipelines.common.config import PipelineConfig
from pipelines.demo.generator import DEMO_LABEL

ECONOMIC_DEMO_SOURCE = "OpenCRE deterministic economic demo"
ECONOMIC_DEMO_SOURCE_URL = (
    "https://github.com/Coolgithub1/opencre-terminal/blob/main/docs/economic.md"
)
ECONOMIC_DEMO_METHODOLOGY = (
    "Five illustrative United States economic series generated from fixed parameters and a "
    "fixed seed. Values are synthetic, deterministic, and not observations from a public source."
)


@dataclass(frozen=True)
class EconomicSeriesDefinition:
    """Parameters for one intentionally synthetic monthly economic time series."""

    key: str
    label: str
    unit: str
    base: float
    trend: float
    amplitude: float
    minimum: float
    maximum: float


SERIES_DEFINITIONS = (
    EconomicSeriesDefinition(
        "unemployment_rate", "Unemployment Rate", "percent", 4.2, -0.008, 0.34, 2.5, 7.0
    ),
    EconomicSeriesDefinition(
        "cpi_annual_change", "CPI Annual Change", "percent", 2.8, -0.003, 0.41, 1.0, 6.0
    ),
    EconomicSeriesDefinition(
        "policy_rate", "Policy Rate", "percent", 4.5, -0.022, 0.28, 0.0, 6.0
    ),
    EconomicSeriesDefinition(
        "nonfarm_payroll_change",
        "Nonfarm Payroll Change",
        "thousand jobs",
        162.0,
        0.12,
        22.0,
        20.0,
        300.0,
    ),
    EconomicSeriesDefinition(
        "construction_spending_change",
        "Construction Spending Change",
        "percent",
        2.5,
        0.006,
        0.73,
        -4.0,
        8.0,
    ),
)


def _month_start(year: int, month: int, offset: int) -> date:
    """Return a month start after a signed offset without a date-library dependency."""
    absolute_month = year * 12 + (month - 1) + offset
    return date(absolute_month // 12, absolute_month % 12 + 1, 1)


def build_economic_history(config: PipelineConfig, months: int = 50) -> pl.DataFrame:
    """Return reproducible monthly indicator rows carrying complete provenance."""
    if months < 2:
        raise ValueError("economic history requires at least two months")
    observed_at = config.retrieved_at
    generated_date = config.generated_at.date()
    rng = np.random.default_rng(config.seed + 800)
    rows: list[dict[str, object]] = []
    for definition_index, definition in enumerate(SERIES_DEFINITIONS):
        previous_value: float | None = None
        for index in range(months):
            observation = _month_start(
                generated_date.year, generated_date.month, index - months + 1
            )
            seasonal = definition.amplitude * np.sin((index + definition_index * 3) / 4.1)
            noise = float(rng.normal(0.0, definition.amplitude / 9))
            value = float(
                np.clip(
                    definition.base + definition.trend * index + seasonal + noise,
                    definition.minimum,
                    definition.maximum,
                )
            )
            rounded_value = round(value, 2)
            change = None if previous_value is None else round(rounded_value - previous_value, 2)
            rows.append(
                {
                    "indicator_key": definition.key,
                    "indicator_name": definition.label,
                    "period_label": observation.strftime("%b %Y"),
                    "previous_value": previous_value,
                    "change": change,
                    "source": ECONOMIC_DEMO_SOURCE,
                    "source_url": ECONOMIC_DEMO_SOURCE_URL,
                    "retrieved_at": observed_at,
                    "observation_date": observation.isoformat(),
                    "metric": definition.key,
                    "value": rounded_value,
                    "unit": definition.unit,
                    "geography": "United States",
                    "methodology": ECONOMIC_DEMO_METHODOLOGY,
                    "data_label": DEMO_LABEL,
                }
            )
            previous_value = rounded_value
    return pl.DataFrame(rows).sort(["indicator_key", "observation_date"])


def latest_economic_indicators(history: pl.DataFrame) -> pl.DataFrame:
    """Select the most recent record for each deterministic indicator."""
    return history.group_by("indicator_key", maintain_order=True).tail(1).sort("indicator_name")
