# Market analytics methodology

Phase 3 creates descriptive, deterministic market analytics from the synthetic Phase 2 time series. This is not a signal engine, investment recommendation, or causal claim.

## Normalization

The default method is **historical percentile** within each market's own 50-month synthetic history. A value at the 90th percentile is greater than or equal to 90% of its recorded synthetic history. Identical values receive the same percentile. The shared normalization module also supports min–max and z-score transformations for future use; neither is used for the Phase 3 outputs.

## Market-state scores

All scores are descriptive 0–100 values calculated from these fixed weights:

| Component | Formula |
| --- | --- |
| Demand | employment-growth percentile × 60% + population-growth percentile × 40% |
| Supply balance | inverse vacancy percentile × 65% + inverse construction-pipeline percentile × 35% |
| Performance | rent-growth percentile × 60% + absorption percentile × 40% |
| Capital activity | transaction-volume percentile |
| Event activity | monthly event-count percentile |
| Market activity | demand × 25% + supply balance × 15% + performance × 30% + capital activity × 20% + event activity × 10% |

`six_month_change` is the difference between the current and six-month-prior market-activity score. Every record identifies its source, retrieval date, observation date, geography, method, metric, unit, and synthetic-data label.

## Rankings

`data/markets/rankings.json` lists five markets in each of these transparent categories: top markets, bottom markets, fastest improving, fastest deteriorating, strongest demand, weakest supply, highest rent momentum, and highest investment activity. Each result exposes the metric used, score, rank, overall activity score, and six-month change.

The generated outputs are `data/markets/market_analytics.parquet`, `data/markets/latest_analytics.json`, and `data/markets/rankings.json`.
