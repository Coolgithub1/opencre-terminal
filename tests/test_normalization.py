import pytest

from pipelines.analytics.normalization import (
    NormalizationError,
    historical_percentile,
    min_max,
    z_score,
)


def test_historical_percentile_is_inclusive_and_keeps_ties_equal():
    assert historical_percentile([1, 2, 3, 3]) == [25.0, 50.0, 100.0, 100.0]


def test_min_max_and_z_score_handle_constant_series():
    assert min_max([7, 7, 7]) == [50.0, 50.0, 50.0]
    assert z_score([7, 7, 7]) == [0.0, 0.0, 0.0]


def test_normalization_rejects_unknown_methods():
    with pytest.raises(NormalizationError, match="Unsupported"):
        from pipelines.analytics.normalization import normalize

        normalize([1, 2, 3], method="opaque")
