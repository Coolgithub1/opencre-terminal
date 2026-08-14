from pathlib import Path

import duckdb

from pipelines.common.config import PipelineConfig
from pipelines.run import run_demo_pipeline
from pipelines.validation import validate_data_directory


def test_pipeline_writes_and_validates_static_data(tmp_path):
    data_dir = tmp_path / "data"
    frontend_data_dir = tmp_path / "frontend-data"
    report = run_demo_pipeline(
        PipelineConfig(output_dir=data_dir, frontend_output_dir=frontend_data_dir)
    )

    assert report["status"] == "healthy"
    assert (data_dir / "index.json").exists()
    assert (data_dir / "metadata/pipeline_status.json").exists()
    assert (data_dir / "events/latest.json").exists()
    assert (data_dir / "events/articles.json").exists()
    assert (data_dir / "events/extracted.json").exists()
    assert (data_dir / "geography/markets.geojson").exists()
    assert (frontend_data_dir / "signals/latest.json").exists()
    assert (frontend_data_dir / "geography/markets.geojson").exists()
    assert (frontend_data_dir / "events/extracted.json").exists()
    assert (frontend_data_dir / "signals/history/charleston-sc.json").exists()
    assert validate_data_directory(data_dir)["status"] == "healthy"

    with duckdb.connect(":memory:") as connection:
        count = connection.execute(
            "SELECT count(*) FROM read_parquet(?)",
            [str(data_dir / "markets/market_metrics.parquet")],
        ).fetchone()[0]
    assert count == 1_000


def test_pipeline_creates_no_database_file(tmp_path):
    data_dir = tmp_path / "data"
    run_demo_pipeline(PipelineConfig(output_dir=data_dir, frontend_output_dir=None))

    assert not list(Path(data_dir).rglob("*.duckdb"))
