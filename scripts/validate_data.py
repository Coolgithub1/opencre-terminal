"""Validate a generated OpenCRE static-data directory."""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from pipelines.common.config import DEFAULT_DATA_DIR
from pipelines.validation import validate_data_directory


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", type=Path, default=DEFAULT_DATA_DIR)
    return parser.parse_args()


if __name__ == "__main__":
    print(validate_data_directory(parse_args().data_dir))
