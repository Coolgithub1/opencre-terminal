import httpx

from pipelines.common.config import PipelineConfig
from pipelines.economic.connectors import run_optional_connectors
from pipelines.economic.demo import build_economic_history, latest_economic_indicators


def test_economic_demo_history_is_complete_deterministic_and_traceable(tmp_path):
    config = PipelineConfig(output_dir=tmp_path)
    history = build_economic_history(config)
    latest = latest_economic_indicators(history)

    assert history.height == 250
    assert latest.height == 5
    assert latest["indicator_key"].n_unique() == 5
    assert latest["data_label"].str.contains("DEMO DATA").all()
    assert latest["change"].is_not_null().all()
    assert history["source"].n_unique() == 1
    assert history["observation_date"].min() == "2022-07-01"
    assert history["observation_date"].max() == "2026-08-01"


def test_optional_connectors_skip_without_credentials_without_making_requests():
    requested: list[str] = []

    def unexpected_request(request: httpx.Request) -> httpx.Response:
        requested.append(str(request.url))
        return httpx.Response(500)

    with httpx.Client(transport=httpx.MockTransport(unexpected_request)) as client:
        results = run_optional_connectors({}, "2026-08-13T23:30:00Z", client)

    assert requested == []
    assert [(result.connector, result.status) for result in results] == [
        ("bls", "skipped"),
        ("census", "skipped"),
        ("fred", "skipped"),
        ("sec", "skipped"),
    ]


def test_optional_connectors_normalize_configured_public_responses():
    def mock_public_api(request: httpx.Request) -> httpx.Response:
        if request.url.host == "api.bls.gov":
            assert request.method == "POST"
            return httpx.Response(
                200,
                json={
                    "Results": {
                        "series": [{"data": [{"year": "2026", "period": "M07", "value": "4.1"}]}]
                    }
                },
            )
        if request.url.host == "api.census.gov":
            return httpx.Response(
                200, json=[["NAME", "DP03_0062E", "us"], ["United States", "3.9", "1"]]
            )
        if request.url.host == "api.stlouisfed.org":
            return httpx.Response(
                200, json={"observations": [{"date": "2026-07-01", "value": "4.33"}]}
            )
        if request.url.host == "data.sec.gov":
            assert request.headers["user-agent"] == "OpenCRE test contact@example.org"
            return httpx.Response(
                200,
                json={
                    "stateOfIncorporationDescription": "Delaware",
                    "filings": {"recent": {"filingDate": ["2026-08-01", "2026-07-30"]}},
                },
            )
        raise AssertionError(f"Unexpected request: {request.url}")

    environment = {
        "BLS_API_KEY": "test-bls-key",
        "CENSUS_API_KEY": "test-census-key",
        "FRED_API_KEY": "test-fred-key",
        "SEC_USER_AGENT": "OpenCRE test contact@example.org",
        "SEC_CIK": "320193",
    }
    with httpx.Client(transport=httpx.MockTransport(mock_public_api)) as client:
        results = run_optional_connectors(environment, "2026-08-13T23:30:00Z", client)

    assert [result.status for result in results] == ["healthy", "healthy", "healthy", "healthy"]
    records = [record for result in results for record in result.records]
    assert [record["indicator_key"] for record in records] == [
        "unemployment_rate",
        "acs_unemployment_rate",
        "federal_funds_rate",
        "sec_recent_filing_count",
    ]
    assert all("PUBLIC SOURCE ARTIFACT" in str(record["data_label"]) for record in records)
    assert all("test-" not in str(record) for record in records)
