# RSS metadata and deterministic events

Phase 7 adds two intentionally separate paths.

## Static terminal fixture

`pipelines/rss/demo.py` creates 20 synthetic RSS metadata records for the existing 20 synthetic markets. The deterministic pipeline writes them to `data/events/articles.json`, runs the rule engine, and writes the 20 resolved results to `data/events/extracted.json` and `data/events/latest.json`. The browser reads those small files only on the Events page. Every record is labeled `DEMO DATA` and must not be treated as reporting, market research, or a claim about an organization or location.

The fixture tests transparent rules for expansion, relocation, closure, layoffs, hiring, facility openings, manufacturing, warehouse, data center, hotel, retail, infrastructure, construction, rezoning, acquisition, sale, lease, financing, and bankruptcy categories. Not every configured event category is represented in the initial 20-record fixture.

## Parser and source policy

The generic parser accepts a reviewed RSS registry in `pipelines/rss/feeds.json`. Each entry declares its publisher, HTTPS feed endpoint, category, active status, license, and source-policy page. The first active entry is the Federal Reserve Board press-release feed, which the Federal Reserve publishes on its [RSS catalogue](https://www.federalreserve.gov/feeds/feeds.htm).

The parser requests only the feed XML. It retains the title, publisher, link, publication date, short feed-provided summary, category, and provenance fields. It removes URL fragments and `utm_*` parameters before deduplication. It never requests linked article pages, parses paywalled material, circumvents access controls, or republishes full-text content.

## Event rules and confidence

`pipelines/rss/events.py` applies visible keyword phrases, configured entity aliases, and exact configured market-name matching. Exact aliases resolve first. Fuzzy aliases are accepted only at a conservative deterministic threshold and only when a single best candidate exists; multiple candidates result in no event. An emitted event requires one event rule, one unambiguous entity, and one unambiguous market.

Confidence is a deterministic score capped at 95%: 45% base, 10% per matched event phrase, 15% for entity resolution, 15% for market association, 5% when a stated dollar amount is parsed, and 5% when a stated job count is parsed. It represents rule completeness, not truth, importance, materiality, or causation.

## Scheduled public feed check

`.github/workflows/rss-ingestion.yml` runs every 30 minutes and on manual dispatch with read-only permissions. It runs `scripts/run_rss_pipeline.py`, which writes normalized metadata, extracted events, and a per-feed status file to a seven-day Actions artifact. The workflow does not commit data, modify the deployed Pages bundle, need a secret, or operate a server. This keeps live publisher metadata auditable and separate from the reproducible demo terminal until a source-review and release process is explicitly approved.
