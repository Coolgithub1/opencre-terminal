"""Load and validate the public RSS feed registry."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

RSS_CATEGORIES = frozenset(
    {
        "CRE",
        "Industrial",
        "Multifamily",
        "Office",
        "Retail",
        "Hotel",
        "Hospitality",
        "Finance",
        "Economy",
        "Manufacturing",
        "Technology",
        "Infrastructure",
        "Government",
    }
)


@dataclass(frozen=True)
class FeedDefinition:
    """A publisher-approved RSS endpoint and its declared handling metadata."""

    name: str
    publisher: str
    url: str
    category: str
    active: bool
    license: str
    source_policy_url: str

    @classmethod
    def from_mapping(cls, value: dict[str, object]) -> FeedDefinition:
        feed = cls(
            name=str(value["name"]),
            publisher=str(value["publisher"]),
            url=str(value["url"]),
            category=str(value["category"]),
            active=bool(value["active"]),
            license=str(value["license"]),
            source_policy_url=str(value["source_policy_url"]),
        )
        if feed.category not in RSS_CATEGORIES:
            raise ValueError(f"{feed.name}: unsupported RSS category {feed.category}")
        if not feed.url.startswith("https://"):
            raise ValueError(f"{feed.name}: RSS URLs must use HTTPS")
        return feed


def load_feed_registry(path: Path) -> tuple[FeedDefinition, ...]:
    """Read a small, reviewable feed registry from JSON."""
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, list) or not all(isinstance(item, dict) for item in payload):
        raise ValueError(f"{path}: expected a JSON array of feed definitions")
    feeds = tuple(FeedDefinition.from_mapping(item) for item in payload)
    if len({feed.url for feed in feeds}) != len(feeds):
        raise ValueError(f"{path}: feed URLs must be unique")
    return feeds
