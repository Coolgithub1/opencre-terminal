from pipelines.analytics.market_state import build_market_analytics
from pipelines.backtesting.engine import build_backtest_results
from pipelines.common.config import PipelineConfig
from pipelines.demo.generator import generate_demo_frames
from pipelines.signals.config import DEFAULT_SIGNAL_DEFINITIONS
from pipelines.signals.engine import build_signal_history


def test_backtest_grid_is_complete_and_non_causal_descriptive():
    frames = generate_demo_frames(PipelineConfig())
    signal_history = build_signal_history(
        build_market_analytics(frames.market_metrics, frames.events), DEFAULT_SIGNAL_DEFINITIONS
    )
    results = build_backtest_results(signal_history, frames.market_metrics)
    all_market_50 = next(result for result in results if result["result_id"] == "all-markets:50:6")
    all_market_70 = next(result for result in results if result["result_id"] == "all-markets:70:6")

    assert len(results) == 234
    assert len({result["result_id"] for result in results}) == 234
    assert all_market_70["sample_size"] <= all_market_50["sample_size"]
    assert all_market_50["sample_size"] > 0
    assert 0 <= all_market_50["hit_rate"] <= 100
    assert 0 <= all_market_50["outcome_percentile"] <= 100
    assert "do not claim causation" in str(all_market_50["methodology"])
