import json

import pytest

from pipelines.common.config import PipelineConfig
from pipelines.run import run_demo_pipeline
from pipelines.validation import DataValidationError, validate_data_directory


def test_validator_rejects_an_incomplete_dataset_index(tmp_path):
    data_dir = tmp_path / "data"
    run_demo_pipeline(PipelineConfig(output_dir=data_dir))
    index_path = data_dir / "index.json"
    index = json.loads(index_path.read_text(encoding="utf-8"))
    index["datasets"] = index["datasets"][1:]
    index_path.write_text(json.dumps(index), encoding="utf-8")

    with pytest.raises(DataValidationError, match="markets is absent"):
        validate_data_directory(data_dir)
