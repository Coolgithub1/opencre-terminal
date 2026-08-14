from pipelines.common.config import PipelineConfig
from pipelines.demo.generator import generate_demo_frames
from pipelines.geography.markets import build_market_geojson


def test_market_geojson_contains_one_valid_point_per_synthetic_market(tmp_path):
    config = PipelineConfig(output_dir=tmp_path)
    geojson = build_market_geojson(generate_demo_frames(config).markets.to_dicts(), config)

    assert geojson["type"] == "FeatureCollection"
    assert len(geojson["features"]) == 20
    assert len({feature["properties"]["market_id"] for feature in geojson["features"]}) == 20
    for feature in geojson["features"]:
        longitude, latitude = feature["geometry"]["coordinates"]
        assert feature["geometry"]["type"] == "Point"
        assert -180 <= longitude <= 180
        assert -90 <= latitude <= 90
        assert feature["properties"]["data_label"].startswith("DEMO DATA")
