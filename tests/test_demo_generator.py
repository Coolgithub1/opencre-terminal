from pipelines.common.config import PipelineConfig
from pipelines.demo.generator import DEMO_LABEL, generate_demo_frames


def test_generator_creates_required_synthetic_record_counts(tmp_path):
    frames = generate_demo_frames(PipelineConfig(output_dir=tmp_path))

    assert frames.markets.height == 20
    assert frames.properties.height == 100
    assert frames.hotels.height == 50
    assert frames.transactions.height == 500
    assert frames.market_metrics.height == 1_000
    assert frames.events.height == 1_000
    assert frames.market_metrics["data_label"].unique().to_list() == [DEMO_LABEL]


def test_generator_is_repeatable_for_the_same_seed(tmp_path):
    configuration = PipelineConfig(output_dir=tmp_path, seed=42)

    first = generate_demo_frames(configuration).market_metrics.head(10).to_dicts()
    second = generate_demo_frames(configuration).market_metrics.head(10).to_dicts()

    assert first == second
