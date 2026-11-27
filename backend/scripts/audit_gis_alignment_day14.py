import asyncio
import json
import math
import sys
from pathlib import Path
from typing import Dict, List, Tuple

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from backend.app.main import predict_raster

# Target farm GPS bounding box locked in frontend/src/data/farmParcels.js (EPSG:4326)
EXPECTED_FARM_BOUNDS: Dict[str, float] = {
    "west": 79.1200,
    "south": 21.1239,
    "east": 79.1461,
    "north": 21.1500,
}

TOLERANCE_DEG = 1e-4  # ~11 meters tolerance at equator


def validate_ring(ring: List[List[float]]) -> Tuple[bool, str]:
    """Verify closed GeoJSON polygon ring, finite numbers, and [lon, lat] order."""
    if len(ring) < 4:
        return False, "Polygon ring has fewer than 4 vertices"
    if ring[0] != ring[-1]:
        return False, "Polygon ring is not closed (first vertex != last vertex)"

    for lon, lat in ring:
        if not (math.isfinite(lon) and math.isfinite(lat)):
            return False, "Non-finite (NaN/Inf) coordinate detected"
        # Guard against swapped [lat, lon] order for Nagpur/India farm region
        if not (-180.0 <= lon <= 180.0 and -90.0 <= lat <= 90.0):
            return False, f"Invalid WGS84 coordinate: ({lon}, {lat})"
        if lon < 60.0 or lat > 40.0:
            return False, f"Possible [lat, lon] axis swap detected: ({lon}, {lat})"

    return True, "OK"


def main() -> None:
    response = asyncio.run(predict_raster(file=None))
    crs = response["crs"]
    features = response["geojson"]["features"]

    assert crs == "EPSG:4326", f"CRS mismatch: expected EPSG:4326, got {crs}"
    assert len(features) > 0, "No GeoJSON features returned by /predict-raster"

    all_lons: List[float] = []
    all_lats: List[float] = []
    invalid_features: List[str] = []

    for feat in features:
        parcel_id = feat["properties"]["parcel_id"]
        ring = feat["geometry"]["coordinates"][0]
        is_valid, reason = validate_ring(ring)
        if not is_valid:
            invalid_features.append(f"{parcel_id}: {reason}")
            continue
        for lon, lat in ring:
            all_lons.append(lon)
            all_lats.append(lat)

    assert not invalid_features, f"Invalid geometries found: {invalid_features}"

    actual_bounds = {
        "west": round(min(all_lons), 6),
        "south": round(min(all_lats), 6),
        "east": round(max(all_lons), 6),
        "north": round(max(all_lats), 6),
    }

    deltas = {
        edge: round(abs(actual_bounds[edge] - EXPECTED_FARM_BOUNDS[edge]), 6)
        for edge in ("west", "south", "east", "north")
    }
    max_delta = max(deltas.values())
    aligned = max_delta <= TOLERANCE_DEG

    assert aligned, f"Spatial misalignment! Max delta={max_delta} deg > {TOLERANCE_DEG} deg"

    audit_report = {
        "audit_day": "Day 14 - GIS Coordinate Alignment Audit",
        "scan_id": response["scan_id"],
        "crs": crs,
        "axis_order": "[longitude, latitude] (GeoJSON RFC 7946 / Deck.gl)",
        "total_features_audited": len(features),
        "valid_closed_polygons": len(features) - len(invalid_features),
        "expected_farm_bounds": EXPECTED_FARM_BOUNDS,
        "actual_geojson_bounds": actual_bounds,
        "boundary_deltas_deg": deltas,
        "max_delta_deg": max_delta,
        "tolerance_deg": TOLERANCE_DEG,
        "alignment_status": "PASS (100% Aligned)",
    }

    report_path = REPO_ROOT / "backend" / "models" / "gis_alignment_audit_day14.json"
    with open(report_path, "w") as f:
        json.dump(audit_report, f, indent=2)

    print("=== DAY 14 GIS COORDINATE ALIGNMENT AUDIT ===")
    print(f"CRS & Axis Order:   {crs} | [lon, lat]")
    print(f"Features Audited:   {len(features)} / {len(features)} valid closed rings")
    print(f"Expected Bounds:    {EXPECTED_FARM_BOUNDS}")
    print(f"Actual Bounds:      {actual_bounds}")
    print(f"Max Boundary Delta: {max_delta} deg (Tolerance: {TOLERANCE_DEG} deg)")
    print(f"Alignment Status:   {audit_report['alignment_status']}")
    print(f"Saved Report ->     {report_path}")


if __name__ == "__main__":
    main()