"""Reproducible numeric normalization methods for auditable market analytics."""

from __future__ import annotations

from collections.abc import Sequence

import numpy as np


class NormalizationError(ValueError):
    """Raised when normalization receives no usable observations."""


def historical_percentile(values: Sequence[float]) -> list[float]:
    """Return inclusive historical percentile ranks on a 0–100 scale.

    Tied values receive the same percentile. This avoids arbitrary ordering and is
    the default because every score can be reproduced from its own history.
    """
    observations = np.asarray(values, dtype=float)
    if observations.size == 0:
        raise NormalizationError("At least one observation is required")
    if not np.isfinite(observations).all():
        raise NormalizationError("Observations must be finite")
    sorted_observations = np.sort(observations)
    return (
        np.searchsorted(sorted_observations, observations, side="right") / observations.size * 100
    ).tolist()


def min_max(values: Sequence[float]) -> list[float]:
    """Scale finite values to 0–100; a constant series maps to neutral 50."""
    observations = np.asarray(values, dtype=float)
    if observations.size == 0:
        raise NormalizationError("At least one observation is required")
    if not np.isfinite(observations).all():
        raise NormalizationError("Observations must be finite")
    lower, upper = observations.min(), observations.max()
    if lower == upper:
        return [50.0] * observations.size
    return ((observations - lower) / (upper - lower) * 100).tolist()


def z_score(values: Sequence[float]) -> list[float]:
    """Return population z-scores; a constant series maps to zero."""
    observations = np.asarray(values, dtype=float)
    if observations.size == 0:
        raise NormalizationError("At least one observation is required")
    if not np.isfinite(observations).all():
        raise NormalizationError("Observations must be finite")
    standard_deviation = observations.std()
    if standard_deviation == 0:
        return [0.0] * observations.size
    return ((observations - observations.mean()) / standard_deviation).tolist()


def normalize(values: Sequence[float], method: str = "historical_percentile") -> list[float]:
    """Normalize a sequence through one explicit supported method."""
    methods = {
        "historical_percentile": historical_percentile,
        "min_max": min_max,
        "z_score": z_score,
    }
    try:
        return methods[method](values)
    except KeyError as error:
        raise NormalizationError(f"Unsupported normalization method: {method}") from error
