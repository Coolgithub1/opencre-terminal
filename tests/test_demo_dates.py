from datetime import date

from pipelines.common.config import PipelineConfig
from pipelines.demo.generator import generate_demo_frames


def test_synthetic_events_do_not_postdate_the_generated_snapshot(tmp_path):
    config = PipelineConfig(output_dir=tmp_path)
    events = generate_demo_frames(config).events

    assert (
        max(date.fromisoformat(value) for value in events["event_date"].to_list())
        <= config.generated_at.date()
    )
