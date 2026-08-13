from dataclasses import replace

import pytest

from pipelines.analytics.market_state import build_market_analytics
from pipelines.common.config import PipelineConfig
from pipelines.demo.generator import generate_demo_frames
from pipelines.signals.config import (
    DEFAULT_SIGNAL_DEFINITIONS,
    SignalComponent,
    SignalConfigurationError,
    validate_signal_definition,
)
from pipelines.signals.engine import (
    build_signal_history,
    build_signal_rankings,
    calculate_signal_record,
    latest_signal_records,
)


def test_signal_configuration_requires_exactly_one_hundred_percent_weight():
    invalid = replace(
        DEFAULT_SIGNAL_DEFINITIONS[0],
        components=(
            SignalComponent("employment", "Employment", "employment_growth_percentile", 99),
        ),
    )

    with pytest.raises(SignalConfigurationError, match="equal 100"):
        validate_signal_definition(invalid)


def test_signal_decomposition_matches_documented_golden_example():
    row = {
        "market_id": "golden-market",
        "market_name": "Golden Market",
        "asset_class": "Industrial",
        "observation_date": "2026-08-01",
        "retrieved_at": "2026-08-13T23:30:00Z",
        "geography": "Golden Market, TS",
        "employment_growth_percentile": 91,
        "rent_growth_percentile": 86,
        "absorption_percentile": 88,
        "vacancy_percentile_inverse": 79,
        "capital_activity_score": 84,
        "construction_percentile_inverse": 71,
    }

    result = calculate_signal_record(row, DEFAULT_SIGNAL_DEFINITIONS[0])

    assert result["score"] == 84.9
    assert result["classification"] == "Strong"
    assert [component["contribution"] for component in result["components"]] == [
        22.75,
        17.2,
        17.6,
        11.85,
        8.4,
        7.1,
    ]


def test_signal_history_and_current_explanations_are_complete(tmp_path):
    frames = generate_demo_frames(PipelineConfig(output_dir=tmp_path))
    analytics = build_market_analytics(frames.market_metrics, frames.events)
    history = build_signal_history(analytics, DEFAULT_SIGNAL_DEFINITIONS)
    latest = latest_signal_records(history, DEFAULT_SIGNAL_DEFINITIONS)
    rankings = build_signal_rankings(latest)

    assert history.height == 1_000
    assert latest.height == 20
    assert history["score"].min() >= 0
    assert history["score"].max() <= 100
    for record in latest.to_dicts():
        assert len(record["components"]) == 6
        assert (
            round(sum(component["contribution"] for component in record["components"]), 4)
            == record["score"]
        )
    assert len(rankings["rankings"]["top_signals"]) == 10
    assert len(rankings["rankings"]["bottom_signals"]) == 10
