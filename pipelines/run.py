"""Orchestrate the deterministic Phase 2 demo-data pipeline."""

from __future__ import annotations

from pathlib import Path

from pipelines.common.config import PipelineConfig
from pipelines.common.io import write_json, write_parquet
from pipelines.demo.generator import (
    DEMO_LABEL,
    METHODOLOGY,
    SOURCE,
    SOURCE_URL,
    generate_demo_frames,
)
from pipelines.schemas import DATASET_SPECS, validate_frame
from pipelines.validation import validate_data_directory


def _dataset_index(config: PipelineConfig) -> dict[str, object]:
    return {
        "schema_version": "1.0.0",
        "data_label": DEMO_LABEL,
        "last_updated": config.retrieved_at,
        "datasets": [
            {
                "name": spec.name,
                "path": spec.relative_path.as_posix(),
                "format": spec.storage,
                "last_updated": config.retrieved_at,
                "record_count": spec.expected_rows,
                "schema_version": "1.0.0",
            }
            for spec in DATASET_SPECS
        ],
    }


def run_demo_pipeline(config: PipelineConfig) -> dict[str, object]:
    """Generate, validate, and describe all Phase 2 data without retaining a database."""
    frames = generate_demo_frames(config)
    frame_by_name = {
        "markets": frames.markets,
        "market_metrics": frames.market_metrics,
        "events": frames.events,
        "transactions": frames.transactions,
        "properties": frames.properties,
        "hotels": frames.hotels,
    }
    output_dir = config.output_dir

    for spec in DATASET_SPECS:
        frame = frame_by_name[spec.name]
        validate_frame(frame, spec)
        output_path = output_dir / spec.relative_path
        if spec.storage == "json":
            write_json(output_path, frame.to_dicts())
        else:
            write_parquet(output_path, frame.to_arrow())

    events = frame_by_name["events"].sort("event_date", descending=True).head(20)
    write_json(output_dir / "events/latest.json", events.to_dicts())
    write_json(output_dir / "index.json", _dataset_index(config))
    write_json(
        output_dir / "metadata/sources.json",
        {
            "data_label": DEMO_LABEL,
            "sources": [
                {
                    "source": SOURCE,
                    "source_url": SOURCE_URL,
                    "license": "Synthetic demo data; no third-party data is included.",
                    "update_frequency": "Generated on demand or in GitHub Actions.",
                    "methodology": METHODOLOGY,
                }
            ],
        },
    )
    write_json(
        output_dir / "metadata/last_updated.json",
        {"last_updated": config.retrieved_at, "data_label": DEMO_LABEL, "schema_version": "1.0.0"},
    )
    write_json(
        output_dir / "metadata/pipeline_status.json",
        {
            "pipeline": "synthetic-demo",
            "status": "healthy",
            "last_updated": config.retrieved_at,
            "data_label": DEMO_LABEL,
            "datasets": [
                {"name": spec.name, "records": spec.expected_rows, "status": "validated"}
                for spec in DATASET_SPECS
            ],
        },
    )

    report = validate_data_directory(output_dir)
    write_json(output_dir / "metadata/validation_report.json", report)
    return report


def default_config(output_dir: Path | None = None) -> PipelineConfig:
    """Return the standard reproducible configuration, optionally targeting another directory."""
    return PipelineConfig() if output_dir is None else PipelineConfig(output_dir=output_dir)
