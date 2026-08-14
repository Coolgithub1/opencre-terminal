from pipelines.common.config import PipelineConfig
from pipelines.demo.generator import generate_demo_frames
from pipelines.rss.demo import build_demo_articles, market_references
from pipelines.rss.events import EntityDefinition, extract_events, resolve_entity
from pipelines.rss.feeds import FeedDefinition
from pipelines.rss.ingest import canonicalize_url, parse_feed_payload


def _feed() -> FeedDefinition:
    return FeedDefinition(
        name="Test feed",
        publisher="Test publisher",
        url="https://example.org/rss.xml",
        category="Economy",
        active=True,
        license="Test license",
        source_policy_url="https://example.org/policy",
    )


def test_rss_parser_canonicalizes_links_and_deduplicates_metadata():
    payload = """<?xml version="1.0"?>
    <rss version="2.0"><channel><title>Test</title>
      <item><title>Older entry</title>
        <link>https://example.org/item?a=1&amp;utm_source=test</link>
        <pubDate>Tue, 01 Jul 2026 10:00:00 GMT</pubDate>
        <description>&lt;b&gt;Short&lt;/b&gt; summary</description></item>
      <item><title>Newer entry</title><link>https://example.org/item?a=1</link>
        <pubDate>Wed, 02 Jul 2026 10:00:00 GMT</pubDate>
        <description>Latest summary</description></item>
    </channel></rss>"""

    articles = parse_feed_payload(payload, _feed(), "2026-08-13T23:30:00Z")

    assert len(articles) == 1
    assert articles[0].title == "Newer entry"
    assert articles[0].url == "https://example.org/item?a=1"
    assert articles[0].description == "Latest summary"
    assert articles[0].published_at == "2026-07-02"
    assert canonicalize_url("https://example.org/a?b=2&utm_campaign=x#a") == "https://example.org/a?b=2"


def test_demo_rss_fixture_extracts_one_traceable_event_per_market(tmp_path):
    config = PipelineConfig(output_dir=tmp_path)
    markets = generate_demo_frames(config).markets.to_dicts()
    articles = build_demo_articles(markets, config)
    events = extract_events(articles, market_references(markets))

    assert len(articles) == 20
    assert len(events) == 20
    assert {event["article_id"] for event in events} == {article.article_id for article in articles}
    assert {event["event_type"] for event in events} >= {
        "corporate_expansion",
        "data_center",
        "hotel_opening",
        "rezoning",
        "financing",
    }
    assert all(event["confidence"] >= 0.9 for event in events)
    assert all(event["amount_usd"] > 0 and event["employment"] > 0 for event in events)


def test_ambiguous_entity_alias_is_not_silently_merged():
    registry = (
        EntityDefinition("Acme East", ("Acme",)),
        EntityDefinition("Acme West", ("Acme",)),
    )

    assert resolve_entity("Acme announces a facility opening", registry) is None
