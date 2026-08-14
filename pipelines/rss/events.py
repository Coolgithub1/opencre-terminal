"""Deterministically resolve entities, markets, and structured events from RSS metadata."""

from __future__ import annotations

import hashlib
import re
from collections.abc import Iterable
from dataclasses import dataclass

from rapidfuzz.fuzz import ratio

from pipelines.rss.ingest import NormalizedArticle

EVENT_METHODOLOGY = (
    "Rule-based extraction matches transparent event phrases, exact aliases, conservative fuzzy "
    "aliases, and configured market names. "
    "Ambiguous entity matches are discarded rather than merged."
)


@dataclass(frozen=True)
class EntityDefinition:
    """One canonical organization and aliases that are safe to resolve."""

    canonical_name: str
    aliases: tuple[str, ...]


@dataclass(frozen=True)
class MarketReference:
    """A static market identifier that can be associated without a spatial database."""

    market_id: str
    market_name: str
    state: str


ENTITY_REGISTRY = (
    EntityDefinition("Northstar Logistics", ("Northstar Logistics", "Northstar")),
    EntityDefinition("Apex Manufacturing", ("Apex Manufacturing", "Apex Mfg")),
    EntityDefinition("Meridian Hospitality", ("Meridian Hospitality", "Meridian Hotels")),
    EntityDefinition("Crescent Retail", ("Crescent Retail", "Crescent Stores")),
    EntityDefinition("Summit Digital", ("Summit Digital", "Summit Data")),
)

EVENT_RULES = (
    ("corporate_expansion", ("corporate expansion", "announces an expansion", "expands")),
    ("corporate_relocation", ("corporate relocation", "relocates headquarters", "relocates")),
    ("corporate_closure", ("corporate closure", "closes a facility", "facility closure")),
    ("layoffs", ("layoffs", "lays off", "workforce reduction")),
    ("hiring", ("hiring", "job creation")),
    ("facility_opening", ("facility opening", "opens a facility", "opens facility")),
    ("manufacturing_investment", ("manufacturing investment", "manufacturing plant")),
    ("warehouse", ("warehouse development", "warehouse facility")),
    ("data_center", ("data center", "datacenter")),
    ("hotel_opening", ("hotel opening", "opens a hotel")),
    ("hotel_closure", ("hotel closure", "closes a hotel")),
    ("retail_opening", ("retail opening", "opens a retail store")),
    ("retail_closure", ("retail closure", "closes a retail store")),
    ("infrastructure", ("infrastructure project", "transit interchange")),
    ("construction", ("construction begins", "groundbreaking")),
    ("rezoning", ("rezoning approved", "rezoning proposal")),
    ("acquisition", ("acquires", "acquisition")),
    ("sale", ("sale completed", "property sale")),
    ("lease", ("lease signed", "lease agreement")),
    ("financing", ("financing secured", "construction financing")),
    ("bankruptcy", ("files for bankruptcy", "bankruptcy filing")),
)


def _normalize(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", value.casefold()).strip()


def resolve_entity(
    text: str, registry: Iterable[EntityDefinition] = ENTITY_REGISTRY
) -> tuple[str, str] | None:
    """Resolve an exact or unique high-confidence alias without merging ambiguous entities."""
    normalized = _normalize(text)
    exact = {
        entity.canonical_name
        for entity in registry
        if any(_normalize(alias) in normalized for alias in entity.aliases)
    }
    if len(exact) == 1:
        return next(iter(exact)), "exact_alias"
    if len(exact) > 1:
        return None
    scored: list[tuple[int, str]] = []
    for entity in registry:
        score = max((ratio(_normalize(alias), normalized) for alias in entity.aliases), default=0)
        if score >= 94:
            scored.append((score, entity.canonical_name))
    scored.sort(reverse=True)
    if len(scored) == 1 or (len(scored) > 1 and scored[0][0] > scored[1][0]):
        return scored[0][1], "fuzzy_alias"
    return None


def resolve_market(text: str, markets: Iterable[MarketReference]) -> MarketReference | None:
    """Associate a mention with one configured market using a deterministic dictionary."""
    normalized = _normalize(text)
    matches = [market for market in markets if _normalize(market.market_name) in normalized]
    if len(matches) != 1:
        return None
    return matches[0]


def _event_match(text: str) -> tuple[str, tuple[str, ...]] | None:
    candidates: list[tuple[int, int, str, tuple[str, ...]]] = []
    for priority, (event_type, phrases) in enumerate(EVENT_RULES):
        matched = tuple(phrase for phrase in phrases if phrase in text)
        if matched:
            candidates.append((len(matched), -priority, event_type, matched))
    if not candidates:
        return None
    _, _, event_type, matched = max(candidates)
    return event_type, matched


def _amount_usd(text: str) -> int:
    match = re.search(r"\$\s*([\d,.]+)\s*(billion|million|m|b)?", text, re.IGNORECASE)
    if not match:
        return 0
    value = float(match.group(1).replace(",", ""))
    multiplier = {"billion": 1_000_000_000, "million": 1_000_000, "m": 1_000_000}.get(
        (match.group(2) or "").casefold(),
        1,
    )
    return round(value * multiplier)


def _employment(text: str) -> int:
    match = re.search(r"([\d,]+)\s+(?:new\s+)?jobs", text, re.IGNORECASE)
    return int(match.group(1).replace(",", "")) if match else 0


def extract_events(
    articles: Iterable[NormalizedArticle], markets: Iterable[MarketReference]
) -> list[dict[str, object]]:
    """Create only events with a rule, unambiguous entity, and configured market association."""
    market_references = tuple(markets)
    events: list[dict[str, object]] = []
    for article in articles:
        raw_text = f"{article.title} {article.description}"
        text = _normalize(raw_text)
        matched_event = _event_match(text)
        entity = resolve_entity(text)
        market = resolve_market(text, market_references)
        if matched_event is None or entity is None or market is None:
            continue
        event_type, phrases = matched_event
        amount_usd = _amount_usd(raw_text)
        employment = _employment(raw_text)
        confidence = min(
            0.95,
            round(
                0.45
                + 0.1 * len(phrases)
                + 0.15
                + 0.15
                + 0.05 * bool(amount_usd)
                + 0.05 * bool(employment),
                2,
            ),
        )
        event_id = hashlib.sha256(f"{article.article_id}|{event_type}".encode()).hexdigest()[:20]
        location = f"{market.market_name}, {market.state}"
        events.append(
            {
                "event_id": f"rss-{event_id}",
                "article_id": article.article_id,
                "event_type": event_type,
                "company": entity[0],
                "entity_resolution": entity[1],
                "market_id": market.market_id,
                "location": location,
                "event_date": article.published_at,
                "amount_usd": amount_usd,
                "employment": employment,
                "confidence": confidence,
                "extraction_rules": list(phrases),
                "article_title": article.title,
                "publisher": article.publisher,
                "url": article.url,
                "published_at": article.published_at,
                "source": article.source,
                "source_url": article.source_url,
                "retrieved_at": article.retrieved_at,
                "observation_date": article.observation_date,
                "metric": "event_count",
                "value": 1.0,
                "unit": "event",
                "geography": location,
                "methodology": EVENT_METHODOLOGY,
                "data_label": article.data_label,
            }
        )
    return sorted(
        events,
        key=lambda event: (str(event["event_date"]), str(event["event_id"])),
        reverse=True,
    )
