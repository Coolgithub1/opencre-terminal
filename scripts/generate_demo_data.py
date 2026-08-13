"""Generate OpenCRE synthetic demo data to the repository data directory."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from pipelines.common.logging import configure_logging
from pipelines.run import default_config, run_demo_pipeline

if __name__ == "__main__":
    configure_logging()
    print(run_demo_pipeline(default_config()))
