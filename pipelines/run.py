"""Orchestrate the deterministic Phase 2 demo-data pipeline."""

from __future__ import annotations

from pathlib import Path

from pipelines.analytics.market_state import build_market_analytics, latest_market_analytics
from pipelines.analytics.rankings import build_rankings
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
from pipelines.signals.config import DEFAULT_SIGNAL_DEFINITIONS, serialize_definitions
from pipelines.signals.engine import (
    SIGNAL_METHODOLOGY,
    SIGNAL_SOURCE,
    SIGNAL_SOURCE_URL,
    build_signal_history,
    build_signal_rankings,
    latest_signal_records,
    signal_explanations,
)
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
        ]
        + [
            {
                "name": "market_rankings",
                "path": "markets/rankings.json",
                "format": "json",
                "last_updated": config.retrieved_at,
                "record_count": 40,
                "schema_version": "1.0.0",
            },
            {
                "name": "signal_rankings",
                "path": "signals/rankings.json",
                "format": "json",
                "last_updated": config.retrieved_at,
                "record_count": 20,
                "schema_version": "1.0.0",
            },
            {
                "name": "signal_explanations",
                "path": "signals/explanations.json",
                "format": "json",
                "last_updated": config.retrieved_at,
                "record_count": 20,
                "schema_version": "1.0.0",
            },
            {
                "name": "signal_configurations",
                "path": "metadata/signal_configs.json",
                "format": "json",
                "last_updated": config.retrieved_at,
                "record_count": len(DEFAULT_SIGNAL_DEFINITIONS),
                "schema_version": "1.0.0",
            },
        ],
    }


def run_demo_pipeline(config: PipelineConfig) -> dict[str, object]:
    """Generate, validate, and describe all Phase 2 data without retaining a database."""
    frames = generate_demo_frames(config)
    market_analytics = build_market_analytics(frames.market_metrics, frames.events)
    latest_analytics = latest_market_analytics(market_analytics)
    rankings = build_rankings(latest_analytics)
    signal_history = build_signal_history(market_analytics, DEFAULT_SIGNAL_DEFINITIONS)
    latest_signals = latest_signal_records(signal_history, DEFAULT_SIGNAL_DEFINITIONS)
    signal_rankings = build_signal_rankings(latest_signals)
    frame_by_name = {
        "markets": frames.markets,
        "market_metrics": frames.market_metrics,
        "events": frames.events,
        "transactions": frames.transactions,
        "properties": frames.properties,
        "hotels": frames.hotels,
        "market_analytics": market_analytics,
        "latest_market_analytics": latest_analytics,
        "signal_history": signal_history,
        "latest_signals": latest_signals,
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
    write_json(output_dir / "markets/rankings.json", rankings)
    write_json(output_dir / "signals/rankings.json", signal_rankings)
    write_json(
        output_dir / "signals/explanations.json", signal_explanations(latest_signals.to_dicts())
    )
    write_json(
        output_dir / "metadata/signal_configs.json",
        {
            "schema_version": "1.0.0",
            "data_label": DEMO_LABEL,
            "source": SIGNAL_SOURCE,
            "source_url": SIGNAL_SOURCE_URL,
            "methodology": SIGNAL_METHODOLOGY,
            "configurations": serialize_definitions(DEFAULT_SIGNAL_DEFINITIONS),
        },
    )
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
                },
                {
                    "source": "OpenCRE deterministic market analytics",
                    "source_url": "https://github.com/Coolgithub1/opencre-terminal/tree/main/docs/analytics.md",
                    "license": "Derived only from OpenCRE synthetic demo data.",
                    "update_frequency": "Generated on demand or in GitHub Actions.",
                    "methodology": (
                        "Historical-percentile normalization and transparent weighted "
                        "descriptive analytics."
                    ),
                },
                {
                    "source": SIGNAL_SOURCE,
                    "source_url": SIGNAL_SOURCE_URL,
                    "license": "Derived only from OpenCRE synthetic demo data.",
                    "update_frequency": "Generated on demand or in GitHub Actions.",
                    "methodology": SIGNAL_METHODOLOGY,
                },
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
            ]
            + [
                {"name": "market_rankings", "records": 40, "status": "validated"},
                {"name": "signal_rankings", "records": 20, "status": "validated"},
                {"name": "signal_explanations", "records": 20, "status": "validated"},
                {
                    "name": "signal_configurations",
                    "records": len(DEFAULT_SIGNAL_DEFINITIONS),
                    "status": "validated",
                },
            ],
        },
    )

    report = validate_data_directory(output_dir)
    write_json(output_dir / "metadata/validation_report.json", report)
    return report


def default_config(output_dir: Path | None = None) -> PipelineConfig:
    """Return the standard reproducible configuration, optionally targeting another directory."""
    return PipelineConfig() if output_dir is None else PipelineConfig(output_dir=output_dir)
