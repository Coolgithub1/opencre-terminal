"""Versioned signal definitions with explicit metrics, weights, and bounds."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from math import isclose


@dataclass(frozen=True)
class SignalComponent:
    """A bounded normalized metric's contribution to a signal."""

    key: str
    label: str
    source_field: str
    weight: float


@dataclass(frozen=True)
class SignalDefinition:
    """One auditable signal model for an asset class."""

    key: str
    name: str
    asset_class: str
    version: str
    components: tuple[SignalComponent, ...]


DEFAULT_COMPONENTS = (
    SignalComponent("employment", "Employment", "employment_growth_percentile", 25),
    SignalComponent("rent_growth", "Rent Growth", "rent_growth_percentile", 20),
    SignalComponent("absorption", "Absorption", "absorption_percentile", 20),
    SignalComponent("vacancy", "Vacancy", "vacancy_percentile_inverse", 15),
    SignalComponent("investment", "Investment", "capital_activity_score", 10),
    SignalComponent("construction", "Construction", "construction_percentile_inverse", 10),
)

DEFAULT_SIGNAL_DEFINITIONS = tuple(
    SignalDefinition(
        key=f"{asset_class.lower()}_growth",
        name=f"{asset_class} Growth",
        asset_class=asset_class,
        version="1.0.0",
        components=DEFAULT_COMPONENTS,
    )
    for asset_class in ("Industrial", "Multifamily", "Office", "Retail", "Hotel")
)


class SignalConfigurationError(ValueError):
    """Raised for a definition that cannot yield a complete 0–100 score."""


def validate_signal_definition(definition: SignalDefinition) -> None:
    """Reject ambiguous configurations before any score is calculated."""
    keys = [component.key for component in definition.components]
    source_fields = [component.source_field for component in definition.components]
    total_weight = sum(component.weight for component in definition.components)
    if not definition.components:
        raise SignalConfigurationError(f"{definition.name}: at least one component is required")
    if len(keys) != len(set(keys)) or len(source_fields) != len(set(source_fields)):
        raise SignalConfigurationError(f"{definition.name}: component fields must be unique")
    if any(component.weight <= 0 for component in definition.components):
        raise SignalConfigurationError(f"{definition.name}: component weights must be positive")
    if not isclose(total_weight, 100, abs_tol=0.000001):
        raise SignalConfigurationError(
            f"{definition.name}: component weights must equal 100, received {total_weight}"
        )


def validate_signal_definitions(definitions: tuple[SignalDefinition, ...]) -> None:
    """Validate the complete registry and its unique asset-class assignment."""
    asset_classes = [definition.asset_class for definition in definitions]
    if len(asset_classes) != len(set(asset_classes)):
        raise SignalConfigurationError("Each asset class must have exactly one signal definition")
    for definition in definitions:
        validate_signal_definition(definition)


def serialize_definitions(definitions: tuple[SignalDefinition, ...]) -> list[dict[str, object]]:
    """Expose signal definitions as static JSON for frontend auditability."""
    validate_signal_definitions(definitions)
    return [asdict(definition) for definition in definitions]
