"""Generate synthetic market-centroid GeoJSON without a spatial database."""

from __future__ import annotations

from typing import Any

from pipelines.common.config import PipelineConfig
from pipelines.demo.generator import DEMO_LABEL

GEOGRAPHY_SOURCE = "OpenCRE static geographic demo dataset"
GEOGRAPHY_SOURCE_URL = "https://github.com/Coolgithub1/opencre-terminal/tree/main/docs/geography.md"
GEOGRAPHY_METHODOLOGY = (
    "Representative city-centroid points used only to demonstrate static browser mapping. "
    "They are not legal market, MSA, submarket, property, county, ZIP, or census-tract boundaries."
)

MARKET_CENTROIDS = {
    "charleston-sc": (-79.9311, 32.7765),
    "columbus-oh": (-82.9988, 39.9612),
    "nashville-tn": (-86.7816, 36.1627),
    "dallas-tx": (-96.7970, 32.7767),
    "phoenix-az": (-112.0740, 33.4484),
    "atlanta-ga": (-84.3880, 33.7490),
    "austin-tx": (-97.7431, 30.2672),
    "denver-co": (-104.9903, 39.7392),
    "miami-fl": (-80.1918, 25.7617),
    "raleigh-nc": (-78.6382, 35.7796),
    "salt-lake-city-ut": (-111.8910, 40.7608),
    "charlotte-nc": (-80.8431, 35.2271),
    "tampa-fl": (-82.4572, 27.9506),
    "las-vegas-nv": (-115.1398, 36.1699),
    "minneapolis-mn": (-93.2650, 44.9778),
    "seattle-wa": (-122.3321, 47.6062),
    "chicago-il": (-87.6298, 41.8781),
    "houston-tx": (-95.3698, 29.7604),
    "san-antonio-tx": (-98.4936, 29.4241),
    "orlando-fl": (-81.3792, 28.5383),
}


def build_market_geojson(
    markets: list[dict[str, Any]], config: PipelineConfig
) -> dict[str, object]:
    """Return one provenance-carrying market-point feature per generated market."""
    features = []
    for market in markets:
        market_id = market["market_id"]
        try:
            longitude, latitude = MARKET_CENTROIDS[market_id]
        except KeyError as error:
            raise ValueError(f"No static geography configured for {market_id}") from error
        features.append(
            {
                "type": "Feature",
                "id": market_id,
                "geometry": {"type": "Point", "coordinates": [longitude, latitude]},
                "properties": {
                    "market_id": market_id,
                    "market_name": market["market_name"],
                    "state": market["state"],
                    "msa": market["msa"],
                    "geography_type": "representative_city_centroid",
                    "source": GEOGRAPHY_SOURCE,
                    "source_url": GEOGRAPHY_SOURCE_URL,
                    "retrieved_at": config.retrieved_at,
                    "observation_date": config.generated_at.date().isoformat(),
                    "metric": "market_centroid",
                    "value": 1,
                    "unit": "feature",
                    "geography": f"{market['market_name']}, {market['state']}",
                    "methodology": GEOGRAPHY_METHODOLOGY,
                    "data_label": DEMO_LABEL,
                },
            }
        )
    return {
        "type": "FeatureCollection",
        "data_label": DEMO_LABEL,
        "source": GEOGRAPHY_SOURCE,
        "source_url": GEOGRAPHY_SOURCE_URL,
        "methodology": GEOGRAPHY_METHODOLOGY,
        "features": features,
    }
