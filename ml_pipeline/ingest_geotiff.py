"""
TerraSpectra — Hyperspectral Data Ingestion & GeoTIFF Spatial Converter
Downloads 200-band hyperspectral agricultural cubes and encodes them into
WGS84 (EPSG:4326) geo-referenced GeoTIFF rasters for downstream 3D-CNN + ViT
training and FastAPI tiled inference.
"""

import os
import requests
import scipy.io as sio
import numpy as np
import rasterio
from rasterio.transform import from_origin


DATASETS = {
    "indian_pines_corrected.mat": [
        "https://github.com/gokriznastic/HybridSN/raw/master/data/Indian_pines_corrected.mat",
        "https://www.ehu.eus/ccwintco/uploads/6/67/Indian_pines_corrected.mat",
    ],
    "indian_pines_gt.mat": [
        "https://github.com/gokriznastic/HybridSN/raw/master/data/Indian_pines_gt.mat",
        "https://www.ehu.eus/ccwintco/uploads/c/c4/Indian_pines_gt.mat",
    ],
}


def download_hyperspectral_data(raw_dir: str = "data/raw") -> tuple[str, str]:
    os.makedirs(raw_dir, exist_ok=True)
    headers = {"User-Agent": "Mozilla/5.0"}

    for filename, url_list in DATASETS.items():
        filepath = os.path.join(raw_dir, filename)
        if os.path.exists(filepath):
            continue
        for url in url_list:
            try:
                resp = requests.get(url, headers=headers, timeout=30)
                resp.raise_for_status()
                with open(filepath, "wb") as f:
                    f.write(resp.content)
                break
            except Exception:
                continue

    return (
        os.path.join(raw_dir, "indian_pines_corrected.mat"),
        os.path.join(raw_dir, "indian_pines_gt.mat"),
    )


def convert_to_geotiff(
    cube_mat_path: str,
    gt_mat_path: str,
    output_dir: str = "data/processed",
    origin_lon: float = 79.1200,
    origin_lat: float = 21.1500,
    pixel_size_deg: float = 0.00018,
) -> tuple[str, str]:
    os.makedirs(output_dir, exist_ok=True)

    cube_data = sio.loadmat(cube_mat_path)["indian_pines_corrected"]
    gt_data = sio.loadmat(gt_mat_path)["indian_pines_gt"]

    # Transpose (H, W, Bands) -> (Bands, H, W) and normalize per band
    cube_bands_first = np.transpose(cube_data, (2, 0, 1)).astype(np.float32)
    band_min = cube_bands_first.min(axis=(1, 2), keepdims=True)
    band_max = cube_bands_first.max(axis=(1, 2), keepdims=True)
    cube_norm = (cube_bands_first - band_min) / (band_max - band_min + 1e-8)

    transform = from_origin(origin_lon, origin_lat, pixel_size_deg, pixel_size_deg)

    cube_tif = os.path.join(output_dir, "terraspectra_hyperspectral_cube.tif")
    with rasterio.open(
        cube_tif,
        "w",
        driver="GTiff",
        height=cube_norm.shape[1],
        width=cube_norm.shape[2],
        count=cube_norm.shape[0],
        dtype="float32",
        crs="EPSG:4326",
        transform=transform,
        compress="lzw",
    ) as dst:
        dst.write(cube_norm)

    gt_tif = os.path.join(output_dir, "terraspectra_ground_truth.tif")
    with rasterio.open(
        gt_tif,
        "w",
        driver="GTiff",
        height=gt_data.shape[0],
        width=gt_data.shape[1],
        count=1,
        dtype="uint8",
        crs="EPSG:4326",
        transform=transform,
        compress="lzw",
    ) as dst:
        dst.write(gt_data.astype(np.uint8), 1)

    return cube_tif, gt_tif


if __name__ == "__main__":
    cube_mat, gt_mat = download_hyperspectral_data()
    cube_tif, gt_tif = convert_to_geotiff(cube_mat, gt_mat)
    print(f"GeoTIFF cube generated: {cube_tif}")
    print(f"GeoTIFF ground truth generated: {gt_tif}")
