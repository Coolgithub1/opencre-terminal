"""Build reproducible, synthetic records for OpenCRE Terminal Phase 2."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from math import sin

import numpy as np
import polars as pl

from pipelines.common.config import PipelineConfig

DEMO_LABEL = "DEMO DATA — synthetic, deterministic, and not real market data."
METHODOLOGY = (
    "Deterministic synthetic demo data generated from a fixed seed for software testing; "
    "it is not an observation of a real market."
)
SOURCE = "OpenCRE synthetic demo generator"
SOURCE_URL = "https://github.com/Coolgithub1/opencre-terminal/tree/main/docs/data-sources.md"

MARKETS = (
    ("charleston-sc", "Charleston", "SC", "Charleston-North Charleston, SC"),
    ("columbus-oh", "Columbus", "OH", "Columbus, OH"),
    ("nashville-tn", "Nashville", "TN", "Nashville-Davidson--Murfreesboro--Franklin, TN"),
    ("dallas-tx", "Dallas", "TX", "Dallas-Fort Worth-Arlington, TX"),
    ("phoenix-az", "Phoenix", "AZ", "Phoenix-Mesa-Chandler, AZ"),
    ("atlanta-ga", "Atlanta", "GA", "Atlanta-Sandy Springs-Roswell, GA"),
    ("austin-tx", "Austin", "TX", "Austin-Round Rock-Georgetown, TX"),
    ("denver-co", "Denver", "CO", "Denver-Aurora-Lakewood, CO"),
    ("miami-fl", "Miami", "FL", "Miami-Fort Lauderdale-West Palm Beach, FL"),
    ("raleigh-nc", "Raleigh", "NC", "Raleigh-Cary, NC"),
    ("salt-lake-city-ut", "Salt Lake City", "UT", "Salt Lake City, UT"),
    ("charlotte-nc", "Charlotte", "NC", "Charlotte-Concord-Gastonia, NC-SC"),
    ("tampa-fl", "Tampa", "FL", "Tampa-St. Petersburg-Clearwater, FL"),
    ("las-vegas-nv", "Las Vegas", "NV", "Las Vegas-Henderson-Paradise, NV"),
    ("minneapolis-mn", "Minneapolis", "MN", "Minneapolis-St. Paul-Bloomington, MN-WI"),
    ("seattle-wa", "Seattle", "WA", "Seattle-Tacoma-Bellevue, WA"),
    ("chicago-il", "Chicago", "IL", "Chicago-Naperville-Elgin, IL-IN-WI"),
    ("houston-tx", "Houston", "TX", "Houston-The Woodlands-Sugar Land, TX"),
    ("san-antonio-tx", "San Antonio", "TX", "San Antonio-New Braunfels, TX"),
    ("orlando-fl", "Orlando", "FL", "Orlando-Kissimmee-Sanford, FL"),
)
PROPERTY_TYPES = ("Industrial", "Multifamily", "Office", "Retail", "Hotel")
EVENT_TYPES = (
    "corporate_expansion",
    "facility_opening",
    "infrastructure",
    "construction",
    "lease",
    "financing",
)


@dataclass(frozen=True)
class DemoFrames:
    """Generated datasets before they are persisted by the pipeline."""

    markets: pl.DataFrame
    market_metrics: pl.DataFrame
    events: pl.DataFrame
    transactions: pl.DataFrame
    properties: pl.DataFrame
    hotels: pl.DataFrame


def _months_ending(periods: int = 50) -> tuple[date, ...]:
    """Return monthly dates ending August 2026 without depending on clock time."""
    year, month = 2026, 8
    dates: list[date] = []
    for _ in range(periods):
        dates.append(date(year, month, 1))
        month -= 1
        if month == 0:
            year, month = year - 1, 12
    return tuple(reversed(dates))


def _provenance(
    config: PipelineConfig,
    observation_date: str,
    geography: str,
    metric: str,
    value: float,
    unit: str,
) -> dict[str, object]:
    return {
        "source": SOURCE,
        "source_url": SOURCE_URL,
        "retrieved_at": config.retrieved_at,
        "observation_date": observation_date,
        "metric": metric,
        "value": round(float(value), 4),
        "unit": unit,
        "geography": geography,
        "methodology": METHODOLOGY,
        "data_label": DEMO_LABEL,
    }


def generate_demo_frames(config: PipelineConfig) -> DemoFrames:
    """Generate all Phase 2 synthetic data frames from one fixed random seed."""
    rng = np.random.default_rng(config.seed)
    market_rows: list[dict[str, object]] = []
    metric_rows: list[dict[str, object]] = []
    property_rows: list[dict[str, object]] = []
    hotel_rows: list[dict[str, object]] = []
    transaction_rows: list[dict[str, object]] = []
    event_rows: list[dict[str, object]] = []
    generated_date = config.generated_at.date().isoformat()

    for market_index, (market_id, market_name, state, msa) in enumerate(MARKETS):
        market_rows.append(
            {
                "market_id": market_id,
                "market_name": market_name,
                "state": state,
                "msa": msa,
                "primary_asset_class": PROPERTY_TYPES[market_index % len(PROPERTY_TYPES)],
                **_provenance(
                    config, generated_date, market_name + ", " + state, "market_entity", 1, "market"
                ),
            }
        )

        for month_index, observation in enumerate(_months_ending()):
            seasonal = sin((month_index / 12) * 6.283185307)
            market_bias = (market_index - 9.5) / 8
            employment_growth = max(
                -2.5, min(7.5, 2.8 + market_bias + seasonal * 0.6 + rng.normal(0, 0.25))
            )
            population_growth = max(-0.5, min(4.5, 1.4 + market_bias / 3 + rng.normal(0, 0.12)))
            rent_growth = max(
                -4.0, min(12.0, 3.6 + market_bias * 0.8 + seasonal * 0.8 + rng.normal(0, 0.4))
            )
            vacancy_rate = max(
                2.0, min(18.0, 7.8 - market_bias * 0.5 + seasonal * 0.4 + rng.normal(0, 0.35))
            )
            absorption = int(
                max(-300_000, 1_400_000 + market_bias * 160_000 + rng.normal(0, 240_000))
            )
            transaction_volume = int(
                max(20_000_000, 320_000_000 + market_bias * 40_000_000 + rng.normal(0, 35_000_000))
            )
            construction_pipeline = int(
                max(100_000, 2_100_000 + market_bias * 190_000 + rng.normal(0, 180_000))
            )
            composite_value = (
                employment_growth * 6 + rent_growth * 4 + (18 - vacancy_rate) * 3
            ) / 13
            metric_rows.append(
                {
                    "market_id": market_id,
                    "market_name": market_name,
                    "asset_class": PROPERTY_TYPES[market_index % len(PROPERTY_TYPES)],
                    "employment_growth": round(float(employment_growth), 4),
                    "population_growth": round(float(population_growth), 4),
                    "rent_growth": round(float(rent_growth), 4),
                    "vacancy_rate": round(float(vacancy_rate), 4),
                    "absorption": absorption,
                    "transaction_volume": transaction_volume,
                    "construction_pipeline": construction_pipeline,
                    **_provenance(
                        config,
                        observation.isoformat(),
                        market_name + ", " + state,
                        "market_snapshot_index",
                        composite_value,
                        "index",
                    ),
                }
            )

        for property_index in range(5):
            property_type = PROPERTY_TYPES[(market_index + property_index) % len(PROPERTY_TYPES)]
            square_feet = int(rng.integers(45_000, 720_000))
            property_id = f"{market_id}-property-{property_index + 1:02d}"
            property_rows.append(
                {
                    "property_id": property_id,
                    "market_id": market_id,
                    "property_name": (
                        f"Synthetic {market_name} {property_type} {property_index + 1}"
                    ),
                    "property_type": property_type,
                    "rentable_square_feet": square_feet,
                    "year_built": int(rng.integers(1985, 2025)),
                    **_provenance(
                        config,
                        generated_date,
                        market_name + ", " + state,
                        "rentable_area",
                        square_feet,
                        "square_feet",
                    ),
                }
            )

        for transaction_index in range(25):
            transaction_number = market_index * 25 + transaction_index + 1
            property_id = f"{market_id}-property-{(transaction_index % 5) + 1:02d}"
            sale_price = int(rng.integers(18_000_000, 310_000_000))
            transaction_date = date(
                2022 + (transaction_index % 4), (transaction_index % 12) + 1, 15
            )
            transaction_rows.append(
                {
                    "transaction_id": f"txn-{transaction_number:04d}",
                    "property_id": property_id,
                    "market_id": market_id,
                    "property_type": PROPERTY_TYPES[
                        (market_index + transaction_index) % len(PROPERTY_TYPES)
                    ],
                    "transaction_date": transaction_date.isoformat(),
                    "sale_price": sale_price,
                    "price_per_square_foot": round(
                        sale_price / int(rng.integers(90_000, 700_000)), 2
                    ),
                    **_provenance(
                        config,
                        transaction_date.isoformat(),
                        market_name + ", " + state,
                        "sale_price",
                        sale_price,
                        "USD",
                    ),
                }
            )

        for event_index in range(50):
            event_number = market_index * 50 + event_index + 1
            event_date = date(
                2023 + (event_index % 3), (event_index % 12) + 1, (event_index % 27) + 1
            )
            event_type = EVENT_TYPES[(market_index + event_index) % len(EVENT_TYPES)]
            event_rows.append(
                {
                    "event_id": f"event-{event_number:04d}",
                    "event_type": event_type,
                    "market_id": market_id,
                    "location": market_name + ", " + state,
                    "event_date": event_date.isoformat(),
                    "company": f"Synthetic Company {event_number:04d}",
                    "employment": int(rng.integers(20, 1_200)),
                    "confidence": 0.95,
                    **_provenance(
                        config,
                        event_date.isoformat(),
                        market_name + ", " + state,
                        "event_count",
                        1,
                        "event",
                    ),
                }
            )

    for hotel_index in range(50):
        market_id, market_name, state, _ = MARKETS[hotel_index % len(MARKETS)]
        rooms = int(rng.integers(80, 420))
        adr = round(float(rng.uniform(115, 310)), 2)
        occupancy = round(float(rng.uniform(0.57, 0.87)), 4)
        hotel_rows.append(
            {
                "hotel_id": f"hotel-{hotel_index + 1:03d}",
                "market_id": market_id,
                "hotel_name": f"Synthetic {market_name} Hotel {hotel_index + 1:02d}",
                "brand": ("Independent", "Select Service", "Full Service")[hotel_index % 3],
                "class": ("Economy", "Midscale", "Upscale", "Luxury")[hotel_index % 4],
                "rooms": rooms,
                "adr": adr,
                "occupancy": occupancy,
                "revpar": round(adr * occupancy, 2),
                **_provenance(
                    config, generated_date, market_name + ", " + state, "rooms", rooms, "keys"
                ),
            }
        )

    return DemoFrames(
        markets=pl.DataFrame(market_rows),
        market_metrics=pl.DataFrame(metric_rows),
        events=pl.DataFrame(event_rows),
        transactions=pl.DataFrame(transaction_rows),
        properties=pl.DataFrame(property_rows),
        hotels=pl.DataFrame(hotel_rows),
    )
