import json
import sys
from pathlib import Path

import numpy as np
import rasterio
from rasterio.transform import from_bounds

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from backend.app.services.tiling_engine import SlidingWindowTilingEngine


def create_sample_geotiff(out_path: Path, height: int = 48, width: int = 48, bands: int = 200) -> None:
    """Create a georeferenced 200-band hyperspectral GeoTIFF cube in EPSG:4326."""
    rng = np.random.default_rng(42)
    # Simulate 3 distinct spectral zones across the farm cube
    cube = rng.normal(loc=2500.0, scale=400.0, size=(bands, height, width)).astype(np.float32)
    cube[:, :16, :] += 1400.0   # High chlorophyll zone
    cube[:, 16:32, :] += 200.0  # Moderate stress zone
    cube[:, 32:, :] -= 1100.0   # Blight anomaly zone

    transform = from_bounds(
        west=79.1200,
        south=21.1239,
        east=79.1461,
        north=21.1500,
        width=width,
        height=height,
    )

    out_path.parent.mkdir(parents=True, exist_ok=True)
    with rasterio.open(
        out_path,
        "w",
        driver="GTiff",
        height=height,
        width=width,
        count=bands,
        dtype="float32",
        crs="EPSG:4326",
        transform=transform,
    ) as dst:
        dst.write(cube)


def main() -> None:
    sample_tif = REPO_ROOT / "data" / "sample_farm_cube_200b.tif"
    sample_geojson = REPO_ROOT / "data" / "sample_stitched_heatmap.geojson"

    create_sample_geotiff(sample_tif)

    engine = SlidingWindowTilingEngine(
        models_dir=REPO_ROOT / "backend" / "models",
        patch_size=15,
        stride=8,
        batch_size=32,
    )
    result = engine.stitch_geotiff_to_geojson(sample_tif)

    assert result["tiling_config"]["stitched_coverage_pct"] == 100.0, "Incomplete spatial stitching!"
    features = result["geojson"]["features"]
    assert len(features) > 0, "No stitched GeoJSON features generated!"

    # Verify GPS bounds alignment
    sample_coords = features[0]["geometry"]["coordinates"][0]
    assert len(sample_coords) == 5, "Polygon ring must be closed (5 vertices)"
    assert 79.10 <= sample_coords[0][0] <= 79.16, f"Longitude out of bounds: {sample_coords[0][0]}"
    assert 21.10 <= sample_coords[0][1] <= 21.16, f"Latitude out of bounds: {sample_coords[0][1]}"

    with open(sample_geojson, "w") as f:
        json.dump(result["geojson"], f, indent=2)

    print("=== DAY 12 SLIDING-WINDOW TILING ENGINE AUDIT ===")
    print(f"Input GeoTIFF:       {sample_tif.name} {result['raster_shape']}")
    print(f"Inference Backend:   {result['tiling_config']['inference_backend']}")
    print(f"Overlapping Tiles:   {result['tiling_config']['total_tiles']} (patch=15, stride=8, overlap=7px)")
    print(f"Stitched Coverage:   {result['tiling_config']['stitched_coverage_pct']}%")
    print(f"Summary Telemetry:   {result['summary_metrics']}")
    print(f"First Tile Polygon:  {sample_coords[0]} -> {sample_coords[2]}")
    print(f"Saved GeoJSON ->     {sample_geojson}")


if __name__ == "__main__":
    main()
