"""Run optional credential-aware public economic connectors as an Actions artifact."""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import UTC, datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from pipelines.common.io import write_json
from pipelines.economic.connectors import run_optional_connectors


def main() -> None:
    """Fetch only configured public-source indicators and retain no credential values."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=Path("economic-output"))
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()
    retrieved_at = datetime.now(UTC).isoformat().replace("+00:00", "Z")
    results = run_optional_connectors(os.environ, retrieved_at)
    serialized = [result.to_dict() for result in results]
    records = [record for result in results for record in result.records]
    status = "partial" if any(result.status == "failed" for result in results) else "healthy"
    write_json(args.output_dir / "indicators.json", records)
    write_json(
        args.output_dir / "status.json",
        {
            "status": status,
            "retrieved_at": retrieved_at,
            "connectors": [
                {key: value for key, value in result.items() if key != "records"}
                for result in serialized
            ],
            "indicator_records": len(records),
        },
    )
    print(json.dumps({"status": status, "connectors": serialized, "records": len(records)}))
    if args.strict and any(result.status == "failed" for result in results):
        raise SystemExit("One or more configured economic connectors failed")


if __name__ == "__main__":
    main()
