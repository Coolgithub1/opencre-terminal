"""Credential-aware, artifact-only connectors for reviewed public economic sources."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from typing import Any

import httpx

BLS_API_URL = "https://api.bls.gov/publicAPI/v2/timeseries/data/"
CENSUS_API_URL = "https://api.census.gov/data/2024/acs/acs1/profile"
FRED_API_URL = "https://api.stlouisfed.org/fred/series/observations"
SEC_SUBMISSIONS_URL = "https://data.sec.gov/submissions/CIK{cik}.json"


@dataclass(frozen=True)
class ConnectorResult:
    """A redacted connector outcome suitable for an Actions artifact."""

    connector: str
    status: str
    detail: str
    records: tuple[dict[str, object], ...] = ()

    def to_dict(self) -> dict[str, object]:
        """Serialize a result without retaining request headers or credential values."""
        payload = asdict(self)
        payload["record_count"] = len(self.records)
        return payload


def _record(
    *,
    indicator_key: str,
    indicator_name: str,
    value: float,
    unit: str,
    observation_date: str,
    source: str,
    source_url: str,
    methodology: str,
    retrieved_at: str,
    geography: str = "United States",
) -> dict[str, object]:
    return {
        "indicator_key": indicator_key,
        "indicator_name": indicator_name,
        "source": source,
        "source_url": source_url,
        "retrieved_at": retrieved_at,
        "observation_date": observation_date,
        "metric": indicator_key,
        "value": value,
        "unit": unit,
        "geography": geography,
        "methodology": methodology,
        "data_label": "PUBLIC SOURCE ARTIFACT -- not included in the GitHub Pages demo bundle.",
    }


def _skipped(connector: str, *required: str) -> ConnectorResult:
    return ConnectorResult(connector, "skipped", f"missing {' and '.join(required)}")


def fetch_bls(
    environment: Mapping[str, str], retrieved_at: str, client: httpx.Client
) -> ConnectorResult:
    """Fetch the latest US unemployment-rate observation using the BLS v2 API."""
    key = environment.get("BLS_API_KEY", "").strip()
    if not key:
        return _skipped("bls", "BLS_API_KEY")
    response = client.post(BLS_API_URL, json={"seriesid": ["LNS14000000"], "registrationkey": key})
    response.raise_for_status()
    data = response.json().get("Results", {}).get("series", [{}])[0].get("data", [])
    observation = next((item for item in data if str(item.get("period", "")).startswith("M")), None)
    if not observation:
        raise ValueError("BLS response did not contain a monthly observation")
    period = str(observation["period"])
    observation_date = f"{observation['year']}-{period[1:]}-01"
    record = _record(
        indicator_key="unemployment_rate",
        indicator_name="Unemployment Rate",
        value=float(observation["value"]),
        unit="percent",
        observation_date=observation_date,
        source="U.S. Bureau of Labor Statistics",
        source_url="https://www.bls.gov/developers/api_signature_v2.htm",
        methodology=(
            "Latest monthly LNS14000000 observation returned by the BLS Public Data API v2."
        ),
        retrieved_at=retrieved_at,
    )
    return ConnectorResult("bls", "healthy", "latest monthly observation", (record,))


def fetch_census(
    environment: Mapping[str, str], retrieved_at: str, client: httpx.Client
) -> ConnectorResult:
    """Fetch a national ACS unemployment-rate profile value from the Census API."""
    key = environment.get("CENSUS_API_KEY", "").strip()
    if not key:
        return _skipped("census", "CENSUS_API_KEY")
    response = client.get(
        CENSUS_API_URL,
        params={"get": "NAME,DP03_0062E", "for": "us:1", "key": key},
    )
    response.raise_for_status()
    payload = response.json()
    if not isinstance(payload, list) or len(payload) < 2:
        raise ValueError("Census response did not contain a data row")
    headers, row = payload[0], payload[1]
    values = dict(zip(headers, row, strict=True))
    record = _record(
        indicator_key="acs_unemployment_rate",
        indicator_name="ACS Unemployment Rate",
        value=float(values["DP03_0062E"]),
        unit="percent",
        observation_date="2024-01-01",
        source="U.S. Census Bureau",
        source_url="https://www.census.gov/data/developers/guidance/api-user-guide.API_Key.html",
        methodology=(
            "National ACS 1-year profile variable DP03_0062E returned by the Census Data API."
        ),
        retrieved_at=retrieved_at,
        geography=str(values.get("NAME", "United States")),
    )
    return ConnectorResult("census", "healthy", "national ACS profile observation", (record,))


def fetch_fred(
    environment: Mapping[str, str], retrieved_at: str, client: httpx.Client
) -> ConnectorResult:
    """Fetch the latest effective federal-funds-rate observation from FRED."""
    key = environment.get("FRED_API_KEY", "").strip()
    if not key:
        return _skipped("fred", "FRED_API_KEY")
    response = client.get(
        FRED_API_URL,
        params={
            "series_id": "FEDFUNDS",
            "api_key": key,
            "file_type": "json",
            "sort_order": "desc",
            "limit": "12",
        },
    )
    response.raise_for_status()
    observations = response.json().get("observations", [])
    observation = next(
        (item for item in observations if item.get("value") not in (".", None)), None
    )
    if not observation:
        raise ValueError("FRED response did not contain a numeric observation")
    record = _record(
        indicator_key="federal_funds_rate",
        indicator_name="Federal Funds Rate",
        value=float(observation["value"]),
        unit="percent",
        observation_date=str(observation["date"]),
        source="Federal Reserve Bank of St. Louis FRED",
        source_url="https://fred.stlouisfed.org/docs/api/fred/series_observations.html",
        methodology="Latest numeric FEDFUNDS observation returned by FRED series observations.",
        retrieved_at=retrieved_at,
    )
    return ConnectorResult("fred", "healthy", "latest FEDFUNDS observation", (record,))


def fetch_sec(
    environment: Mapping[str, str], retrieved_at: str, client: httpx.Client
) -> ConnectorResult:
    """Fetch a company filing-count metadata indicator from EDGAR submissions."""
    user_agent = environment.get("SEC_USER_AGENT", "").strip()
    cik = environment.get("SEC_CIK", "").strip()
    if not user_agent or not cik:
        missing = tuple(
            name
            for name, value in (("SEC_USER_AGENT", user_agent), ("SEC_CIK", cik))
            if not value
        )
        return _skipped("sec", *missing)
    normalized_cik = cik.zfill(10)
    response = client.get(
        SEC_SUBMISSIONS_URL.format(cik=normalized_cik),
        headers={"User-Agent": user_agent, "Accept-Encoding": "gzip, deflate"},
    )
    response.raise_for_status()
    payload: dict[str, Any] = response.json()
    recent = payload.get("filings", {}).get("recent", {})
    filing_dates = recent.get("filingDate", [])
    if not isinstance(filing_dates, list):
        raise ValueError("SEC response did not contain recent filing dates")
    record = _record(
        indicator_key="sec_recent_filing_count",
        indicator_name="Recent EDGAR Filing Count",
        value=float(len(filing_dates)),
        unit="filings",
        observation_date=str(filing_dates[0]) if filing_dates else retrieved_at[:10],
        source="U.S. Securities and Exchange Commission EDGAR",
        source_url="https://www.sec.gov/search-filings/edgar-application-programming-interfaces",
        methodology=(
            "Count of current entries in an issuer's EDGAR submissions recent-filings array."
        ),
        retrieved_at=retrieved_at,
        geography=str(payload.get("stateOfIncorporationDescription") or "Issuer filing metadata"),
    )
    return ConnectorResult("sec", "healthy", "recent filing metadata", (record,))


def run_optional_connectors(
    environment: Mapping[str, str],
    retrieved_at: str | None = None,
    client: httpx.Client | None = None,
) -> list[ConnectorResult]:
    """Run configured connectors, skipping missing credentials without network access."""
    observed_at = retrieved_at or datetime.now(UTC).isoformat().replace("+00:00", "Z")
    connector_functions = (fetch_bls, fetch_census, fetch_fred, fetch_sec)

    def run_with(active_client: httpx.Client) -> list[ConnectorResult]:
        results: list[ConnectorResult] = []
        for function in connector_functions:
            try:
                results.append(function(environment, observed_at, active_client))
            except (httpx.HTTPError, KeyError, TypeError, ValueError) as error:
                results.append(
                    ConnectorResult(function.__name__.removeprefix("fetch_"), "failed", str(error))
                )
        return results

    if client is not None:
        return run_with(client)
    with httpx.Client(timeout=20.0, follow_redirects=True) as configured_client:
        return run_with(configured_client)
