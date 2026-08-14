"""Run the opt-in live RSS metadata fetcher and emit static JSON artifacts."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import UTC, datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from pipelines.common.io import write_json
from pipelines.demo.generator import MARKETS
from pipelines.rss.demo import market_references
from pipelines.rss.events import extract_events
from pipelines.rss.feeds import load_feed_registry
from pipelines.rss.ingest import ingest_active_feeds


def main() -> None:
    """Fetch only active, configured RSS XML endpoints and report results transparently."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--registry", type=Path, default=Path("pipelines/rss/feeds.json"))
    parser.add_argument("--output-dir", type=Path, default=Path("rss-output"))
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()
    retrieved_at = datetime.now(UTC).isoformat().replace("+00:00", "Z")
    feeds = load_feed_registry(args.registry)
    articles, report = ingest_active_feeds(feeds, retrieved_at)
    markets = [
        {"market_id": market_id, "market_name": market_name, "state": state}
        for market_id, market_name, state, _ in MARKETS
    ]
    events = extract_events(articles, market_references(markets))
    write_json(args.output_dir / "articles.json", [article.to_dict() for article in articles])
    write_json(args.output_dir / "events.json", events)
    write_json(
        args.output_dir / "status.json",
        {
            "status": (
                "partial" if any(item["status"] == "failed" for item in report) else "healthy"
            ),
            "retrieved_at": retrieved_at,
            "feeds": report,
            "article_records": len(articles),
            "event_records": len(events),
        },
    )
    print(json.dumps({"feeds": report, "articles": len(articles), "events": len(events)}))
    if args.strict and any(item["status"] == "failed" for item in report):
        raise SystemExit("One or more active RSS feeds failed")


if __name__ == "__main__":
    main()
