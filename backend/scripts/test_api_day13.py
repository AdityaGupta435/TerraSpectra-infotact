import sys
from pathlib import Path

from fastapi.testclient import TestClient

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from backend.app.main import app


def main() -> None:
    client = TestClient(app)

    # 1. Health Check
    r_health = client.get("/health")
    assert r_health.status_code == 200
    print("1. GET /health          ->", r_health.json())

    # 2. Predict Raster (Default GeoTIFF cube)
    r_predict = client.post("/predict-raster")
    assert r_predict.status_code == 200
    p_data = r_predict.json()
    assert p_data["geojson"]["type"] == "FeatureCollection"
    assert len(p_data["geojson"]["features"]) > 0
    print(
        f"2. POST /predict-raster -> scan_id={p_data['scan_id']}, "
        f"tiles={len(p_data['geojson']['features'])}, "
        f"coverage={p_data['tiling_config']['stitched_coverage_pct']}%"
    )

    # 3. Farm Analytics
    r_analytics = client.get("/farm-analytics")
    assert r_analytics.status_code == 200
    a_data = r_analytics.json()
    print(
        f"3. GET /farm-analytics  -> total_ha={a_data['total_hectares']}, "
        f"at_risk_ha={a_data['at_risk_hectares']}, "
        f"crops={len(a_data['crop_breakdown'])}, "
        f"anomalies={len(a_data['spectral_anomalies'])}"
    )

    # 4. Historical Trend
    r_trend = client.get("/historical-trend")
    assert r_trend.status_code == 200
    t_data = r_trend.json()
    assert len(t_data["timeline"]) == 4
    print(
        f"4. GET /historical-trend -> points={len(t_data['timeline'])} "
        f"({t_data['timeline'][0]['label']} -> {t_data['timeline'][-1]['label']})"
    )

    print("\nALL DAY 13 FASTAPI ENDPOINTS VERIFIED SUCCESSFULLY!")


if __name__ == "__main__":
    main()