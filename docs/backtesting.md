# Backtesting and historical association

The static terminal offers a selectable grid of deterministic historical-association summaries in `data/backtesting/results.json`. Every row is calculated only from the existing synthetic signal history and synthetic market metrics. It is labeled **DEMO DATA — synthetic, deterministic, and not real market data**.

For each market, asset class, or all-market scope, the engine selects signal observations at or above 50, 60, or 70. It then observes the same synthetic market's rent-growth value three, six, or twelve months later. Each summary includes sample size, mean, median, population standard deviation, outcome percentile, and hit rate. Hit rate means the selected observation's forward outcome was above the all-market median outcome at the same horizon.

This is a descriptive retrospective comparison. It does not establish causation, forecast a return, recommend an investment, or validate a real-world strategy. Results with no qualifying observations show zero sample size and zero summary metrics rather than an implied outcome.

The `backtesting.yml` workflow regenerates the deterministic result file daily as a read-only seven-day Actions artifact. The regular static build produces the exact same result file for GitHub Pages, so the browser performs filtering only and never runs a backtest against hidden or live data.
