"""Publish generated static data into the Vite public directory for GitHub Pages."""

from __future__ import annotations

import shutil
from pathlib import Path


def publish_frontend_datasets(data_dir: Path, frontend_data_dir: Path) -> int:
    """Copy generated datasets verbatim into the versioned static frontend data namespace."""
    copied_files = 0
    for source_path in data_dir.rglob("*"):
        if not source_path.is_file():
            continue
        destination = frontend_data_dir / source_path.relative_to(data_dir)
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source_path, destination)
        copied_files += 1
    return copied_files
