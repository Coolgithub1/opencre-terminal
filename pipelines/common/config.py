"""Configuration that keeps synthetic demo output deterministic and reproducible."""

from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DATA_DIR = REPOSITORY_ROOT / "data"
DEFAULT_FRONTEND_DATA_DIR = REPOSITORY_ROOT / "frontend" / "public" / "data" / "v1"
DEFAULT_SEED = 20_260_813
DEFAULT_GENERATED_AT = datetime(2026, 8, 13, 23, 30, tzinfo=UTC)


@dataclass(frozen=True)
class PipelineConfig:
    """Immutable configuration for a reproducible local or Actions run."""

    output_dir: Path = DEFAULT_DATA_DIR
    frontend_output_dir: Path | None = DEFAULT_FRONTEND_DATA_DIR
    seed: int = DEFAULT_SEED
    generated_at: datetime = DEFAULT_GENERATED_AT

    @property
    def retrieved_at(self) -> str:
        return self.generated_at.isoformat().replace("+00:00", "Z")
