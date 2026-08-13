from pipelines.analytics.market_state import build_market_analytics, latest_market_analytics
from pipelines.analytics.rankings import RANKING_DEFINITIONS, build_rankings
from pipelines.common.config import PipelineConfig
from pipelines.demo.generator import generate_demo_frames


def test_market_analytics_are_bounded_and_have_one_current_market_record(tmp_path):
    frames = generate_demo_frames(PipelineConfig(output_dir=tmp_path))
    history = build_market_analytics(frames.market_metrics, frames.events)
    latest = latest_market_analytics(history)

    assert history.height == 1_000
    assert latest.height == 20
    for field in (
        "demand_score",
        "supply_balance_score",
        "performance_score",
        "capital_activity_score",
        "event_activity_score",
        "market_activity_score",
    ):
        assert history[field].min() >= 0
        assert history[field].max() <= 100
    assert latest["observation_date"].unique().to_list() == ["2026-08-01"]


def test_rankings_are_complete_and_auditable(tmp_path):
    frames = generate_demo_frames(PipelineConfig(output_dir=tmp_path))
    latest = latest_market_analytics(build_market_analytics(frames.market_metrics, frames.events))
    rankings = build_rankings(latest)

    assert set(rankings["rankings"]) == set(RANKING_DEFINITIONS)
    for entries in rankings["rankings"].values():
        assert len(entries) == 5
        assert [entry["rank"] for entry in entries] == [1, 2, 3, 4, 5]
        assert all(entry["data_label"].startswith("DEMO DATA") for entry in entries)
