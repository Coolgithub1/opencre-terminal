"""Generate a deterministic RSS fixture so the static terminal works immediately after cloning."""

from __future__ import annotations

import hashlib
from datetime import timedelta
from typing import Any

from pipelines.common.config import PipelineConfig
from pipelines.demo.generator import DEMO_LABEL
from pipelines.rss.events import MarketReference
from pipelines.rss.ingest import NormalizedArticle

RSS_DEMO_SOURCE = "OpenCRE synthetic RSS fixture"
RSS_DEMO_SOURCE_URL = "https://github.com/Coolgithub1/opencre-terminal/tree/main/docs/rss.md"
RSS_DEMO_METHODOLOGY = (
    "Deterministic synthetic RSS feed metadata used to test parsing, deduplication, "
    "entity resolution, market association, and rule-based event extraction. "
    "It is not reporting or an observation of real events."
)

EVENT_BLUEPRINTS = (
    ("corporate expansion", "Northstar Logistics", "CRE"),
    ("relocates headquarters", "Apex Manufacturing", "Manufacturing"),
    ("closes a facility", "Crescent Retail", "Retail"),
    ("lays off", "Northstar Logistics", "Industrial"),
    ("hiring", "Summit Digital", "Technology"),
    ("opens a facility", "Apex Manufacturing", "Manufacturing"),
    ("manufacturing investment", "Apex Manufacturing", "Manufacturing"),
    ("warehouse development", "Northstar Logistics", "Industrial"),
    ("data center", "Summit Digital", "Technology"),
    ("hotel opening", "Meridian Hospitality", "Hospitality"),
    ("hotel closure", "Meridian Hospitality", "Hotel"),
    ("retail opening", "Crescent Retail", "Retail"),
    ("retail closure", "Crescent Retail", "Retail"),
    ("infrastructure project", "Apex Manufacturing", "Infrastructure"),
    ("construction begins", "Northstar Logistics", "CRE"),
    ("rezoning approved", "Crescent Retail", "Government"),
    ("acquires", "Meridian Hospitality", "Finance"),
    ("sale completed", "Crescent Retail", "CRE"),
    ("lease signed", "Northstar Logistics", "Office"),
    ("financing secured", "Summit Digital", "Finance"),
)


def market_references(markets: list[dict[str, Any]]) -> tuple[MarketReference, ...]:
    """Convert the public market registry into resolver-friendly records."""
    return tuple(
        MarketReference(
            market_id=str(market["market_id"]),
            market_name=str(market["market_name"]),
            state=str(market["state"]),
        )
        for market in markets
    )


def build_demo_articles(
    markets: list[dict[str, Any]], config: PipelineConfig
) -> list[NormalizedArticle]:
    """Return one synthetic, provenance-carrying RSS article per configured market."""
    if len(markets) != len(EVENT_BLUEPRINTS):
        raise ValueError("RSS demo blueprints must match the 20 synthetic markets")
    articles: list[NormalizedArticle] = []
    blueprint_rows = zip(markets, EVENT_BLUEPRINTS, strict=True)
    for index, (market, blueprint) in enumerate(blueprint_rows, start=1):
        phrase, company, category = blueprint
        market_name = str(market["market_name"])
        state = str(market["state"])
        published_at = (config.generated_at.date() - timedelta(days=index * 5)).isoformat()
        title = f"{company} {phrase} in {market_name}, {state}"
        description = (
            f"Synthetic disclosure: {company} {phrase} in {market_name}, {state}, with "
            f"${80 + index * 7} million of planned activity and {90 + index * 11} new jobs."
        )
        url = f"{RSS_DEMO_SOURCE_URL}#rss-demo-{index:02d}"
        article_id = hashlib.sha256(url.encode()).hexdigest()[:20]
        articles.append(
            NormalizedArticle(
                article_id=article_id,
                title=title,
                publisher=RSS_DEMO_SOURCE,
                url=url,
                published_at=published_at,
                description=description,
                category=category,
                feed_name="OpenCRE deterministic RSS fixture",
                source=RSS_DEMO_SOURCE,
                source_url=RSS_DEMO_SOURCE_URL,
                retrieved_at=config.retrieved_at,
                observation_date=published_at,
                metric="rss_article",
                value=1.0,
                unit="article",
                geography=f"{market_name}, {state}",
                methodology=RSS_DEMO_METHODOLOGY,
                data_label=DEMO_LABEL,
            )
        )
    return articles
