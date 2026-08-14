# Public economic connectors

## Static terminal baseline

The GitHub Pages terminal displays five illustrative United States indicators in `data/economic/latest.json`, with 50 monthly points per indicator in `data/economic/history.parquet`. They are created by `pipelines/economic/demo.py` using the project's fixed seed and timestamp. They are **DEMO DATA — synthetic, deterministic, and not real market data**. They are not estimates, forecasts, or copies of BLS, Census, FRED, SEC, or any other public-source values.

## Optional Actions artifact

`scripts/run_economic_pipeline.py` runs a narrow connector registry for BLS, Census, FRED, and SEC. Its only intended execution environment is the read-only `economic-data.yml` GitHub Actions workflow. It writes normalized records and connector health to a seven-day Actions artifact; it does not write to `data/`, commit changes, or alter the GitHub Pages bundle.

Each normalized live record includes source, source URL, retrieval timestamp, observation date, metric, value, unit, geography, methodology, and an explicit public-artifact label. Connector status intentionally reports no request headers, API keys, or request URLs containing credentials.

| Connector | Required GitHub Actions secrets | Narrow initial retrieval |
| --- | --- | --- |
| BLS | `BLS_API_KEY` | Latest `LNS14000000` monthly unemployment-rate observation through the [BLS Public Data API v2](https://www.bls.gov/developers/api_signature_v2.htm). |
| Census | `CENSUS_API_KEY` | National 2024 ACS 1-year profile variable `DP03_0062E`. The [Census API guide](https://www.census.gov/data/developers/guidance/api-user-guide.API_Key.html) documents registered-key use. |
| FRED | `FRED_API_KEY` | Latest numeric `FEDFUNDS` observation via [FRED series observations](https://fred.stlouisfed.org/docs/api/fred/series_observations.html). |
| SEC | `SEC_USER_AGENT`, `SEC_CIK` | Recent-filing count from the configured issuer's EDGAR submissions metadata. The [SEC developer API guidance](https://www.sec.gov/search-filings/edgar-application-programming-interfaces) requires an identifying user agent. |

Missing secrets produce a `skipped` status and make no network call. A configured connector error becomes a per-source `failed` status while the other sources continue; `--strict` causes the script to fail only when a configured source fails. This permits a repository fork to run safely with no secrets while preserving a transparent activation path for a maintainer.

## Activation and source governance

1. Add only the required values above as repository or environment GitHub Actions secrets. Never commit them, put them in a `.env` file, log them, or expose them to the frontend.
2. Review each provider's current terms, rate limits, attribution requirements, and allowed use before enabling it. The workflow is scheduled daily and has read-only repository permissions.
3. Review the artifact and its source provenance before promoting any public data to a future release bundle. Such a promotion needs its own documented license, validation, transformation, and update policy.

The first SEC connector purposefully provides filing-activity metadata rather than an economic estimate. It demonstrates compliant identifier-based access while leaving financial-statement interpretation and issuer selection as explicit future governance work.
