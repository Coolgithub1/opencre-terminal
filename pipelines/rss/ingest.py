"""Fetch RSS XML and retain only normalized feed metadata, never article bodies."""

from __future__ import annotations

import hashlib
import re
from collections.abc import Iterable
from dataclasses import asdict, dataclass
from datetime import UTC, date, datetime
from html import unescape
from time import struct_time
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

import feedparser
import httpx

from pipelines.rss.feeds import FeedDefinition

RSS_METHODOLOGY = (
    "RSS XML is fetched from publisher-declared endpoints only. The pipeline stores a title, "
    "link, publication date, and short feed summary; it never fetches or republishes "
    "article bodies. "
    "Duplicate canonical links are removed deterministically."
)


@dataclass(frozen=True)
class NormalizedArticle:
    """The static metadata contract created from a single RSS entry."""

    article_id: str
    title: str
    publisher: str
    url: str
    published_at: str
    description: str
    category: str
    feed_name: str
    source: str
    source_url: str
    retrieved_at: str
    observation_date: str
    metric: str
    value: float
    unit: str
    geography: str
    methodology: str
    data_label: str

    def to_dict(self) -> dict[str, object]:
        """Serialize the record without leaking parser-specific objects."""
        return asdict(self)


def canonicalize_url(value: str) -> str:
    """Remove fragments and common tracking parameters without fetching the link."""
    parsed = urlsplit(value.strip())
    query = sorted(
        (key, item)
        for key, item in parse_qsl(parsed.query, keep_blank_values=True)
        if not key.casefold().startswith("utm_")
    )
    return urlunsplit((parsed.scheme, parsed.netloc, parsed.path, urlencode(query), ""))


def _clean_text(value: object) -> str:
    text = unescape(str(value or ""))
    text = re.sub(r"<[^>]*>", " ", text)
    return re.sub(r"\s+", " ", text).strip()[:600]


def _entry_date(entry: dict[str, object], retrieved_at: str) -> str:
    parsed = entry.get("published_parsed") or entry.get("updated_parsed")
    if isinstance(parsed, struct_time):
        return date(parsed.tm_year, parsed.tm_mon, parsed.tm_mday).isoformat()
    return retrieved_at[:10]


def parse_feed_payload(
    payload: str, feed: FeedDefinition, retrieved_at: str
) -> list[NormalizedArticle]:
    """Parse XML into a bounded, normalized metadata-only article list."""
    parsed = feedparser.parse(payload)
    articles: list[NormalizedArticle] = []
    for entry in parsed.entries:
        title = _clean_text(entry.get("title"))
        url = canonicalize_url(str(entry.get("link", "")))
        if not title or not url:
            continue
        published_at = _entry_date(entry, retrieved_at)
        article_id = hashlib.sha256(f"{feed.url}|{url}".encode()).hexdigest()[:20]
        articles.append(
            NormalizedArticle(
                article_id=article_id,
                title=title,
                publisher=feed.publisher,
                url=url,
                published_at=published_at,
                description=_clean_text(entry.get("summary") or entry.get("description")),
                category=feed.category,
                feed_name=feed.name,
                source=feed.publisher,
                source_url=feed.url,
                retrieved_at=retrieved_at,
                observation_date=published_at,
                metric="rss_article",
                value=1.0,
                unit="article",
                geography="United States",
                methodology=RSS_METHODOLOGY,
                data_label="PUBLIC RSS METADATA -- publisher-provided headlines and summaries.",
            )
        )
    return deduplicate_articles(articles)


def deduplicate_articles(articles: Iterable[NormalizedArticle]) -> list[NormalizedArticle]:
    """Keep the newest deterministic representation of each canonical article URL."""
    unique: dict[str, NormalizedArticle] = {}
    for article in articles:
        key = article.url.casefold()
        existing = unique.get(key)
        if existing is None or (article.published_at, article.article_id) > (
            existing.published_at,
            existing.article_id,
        ):
            unique[key] = article
    return sorted(
        unique.values(),
        key=lambda article: (article.published_at, article.article_id),
        reverse=True,
    )


def fetch_feed(
    feed: FeedDefinition, retrieved_at: str, client: httpx.Client
) -> list[NormalizedArticle]:
    """Fetch one configured XML endpoint with a small, transparent user agent."""
    response = client.get(
        feed.url,
        headers={
            "User-Agent": "Mozilla/5.0 (compatible; OpenCRE Terminal RSS/0.7; +https://github.com/Coolgithub1/opencre-terminal)"
        },
    )
    response.raise_for_status()
    return parse_feed_payload(response.text, feed, retrieved_at)


def ingest_active_feeds(
    feeds: Iterable[FeedDefinition], retrieved_at: str | None = None
) -> tuple[list[NormalizedArticle], list[dict[str, object]]]:
    """Fetch active feeds and report failures without hiding per-source provenance."""
    observed_at = retrieved_at or datetime.now(UTC).isoformat().replace("+00:00", "Z")
    articles: list[NormalizedArticle] = []
    report: list[dict[str, object]] = []
    with httpx.Client(timeout=20.0, follow_redirects=True) as client:
        for feed in feeds:
            if not feed.active:
                continue
            try:
                fetched = fetch_feed(feed, observed_at, client)
            except httpx.HTTPError as error:
                report.append({"feed": feed.name, "status": "failed", "detail": str(error)})
                continue
            articles.extend(fetched)
            report.append({"feed": feed.name, "status": "healthy", "records": len(fetched)})
    return deduplicate_articles(articles), report
