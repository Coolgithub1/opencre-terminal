# Signal methodology

Phase 4 produces configurable, deterministic market-growth signals from Phase 3 synthetic market analytics. Signals are reproducible weighted scores, not forecasts, investment advice, or causal claims.

## Configuration

The versioned registry is published in `data/metadata/signal_configs.json`. It has one `1.0.0` configuration for each current asset class: Industrial, Multifamily, Office, Retail, and Hotel. Configurations are validated before use: components must be unique, weights must be positive, and total weight must equal exactly 100%.

Each default configuration uses the same audited component scheme:

| Component | Source metric | Weight |
| --- | --- | ---: |
| Employment | employment-growth historical percentile | 25% |
| Rent Growth | rent-growth historical percentile | 20% |
| Absorption | absorption historical percentile | 20% |
| Vacancy | inverse vacancy historical percentile | 15% |
| Investment | transaction-volume historical percentile | 10% |
| Construction | inverse construction-pipeline historical percentile | 10% |

## Formula and classifications

`signal score = Σ(component score × component weight / 100)`

Scores have one non-overlapping label: `Weak` below 30, `Neutral` from 30 to under 50, `Emerging` from 50 to under 70, `Strong` from 70 to under 85, and `Exceptional` from 85 to 100.

For example, the golden test decomposition is: employment `91 × 25% = 22.75`; rent growth `86 × 20% = 17.20`; absorption `88 × 20% = 17.60`; vacancy `79 × 15% = 11.85`; investment `84 × 10% = 8.40`; construction `71 × 10% = 7.10`; total `84.90` (`Strong`).

## Static outputs

- `data/signals/history.parquet` — one scored observation for every market-month.
- `data/signals/latest.json` — current score and machine-readable component decomposition for every market.
- `data/signals/explanations.json` — compact current explanation records for a future terminal panel.
- `data/signals/rankings.json` — top and bottom ten signals.

The frontend will display these decompositions in Phase 5. No score is hidden behind an AI model or external service.
