"""Run the deterministic Phase 2 dataset pipeline, optionally in a target directory."""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from pipelines.common.logging import configure_logging
from pipelines.run import default_config, run_demo_pipeline


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output-dir", type=Path, help="Directory that will receive generated static datasets."
    )
    return parser.parse_args()


if __name__ == "__main__":
    configure_logging()
    args = parse_args()
    print(run_demo_pipeline(default_config(args.output_dir)))
