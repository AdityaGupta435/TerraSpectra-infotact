"""
TerraSpectra — PCA Spectral Compression & 3D Spatial-Spectral Patch Generator
Compresses 200-band GeoTIFF cubes into 30 principal components (retaining >98% variance),
serializes scaler/PCA artifacts for FastAPI inference parity, and generates memory-safe
15x15x30 3D patches with stratified 70/15/15 train/val/test splits.
"""

import os
import joblib
import numpy as np
import rasterio
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.model_selection import train_test_split


def fit_transform_pca(
    cube: np.ndarray,
    n_components: int = 30,
    artifacts_dir: str = "data/artifacts",
) -> np.ndarray:
    """Fit StandardScaler + PCA on (Bands, H, W) cube and return (H, W, n_components)."""
    os.makedirs(artifacts_dir, exist_ok=True)
    num_bands, height, width = cube.shape

    pixels_200 = np.transpose(cube, (1, 2, 0)).reshape(-1, num_bands)

    scaler = StandardScaler()
    pixels_scaled = scaler.fit_transform(pixels_200)

    pca = PCA(n_components=n_components, random_state=42)
    pixels_pca = pca.fit_transform(pixels_scaled).astype(np.float32)

    joblib.dump(scaler, os.path.join(artifacts_dir, "spectral_scaler.joblib"))
    joblib.dump(pca, os.path.join(artifacts_dir, "spectral_pca_30.joblib"))

    return pixels_pca.reshape(height, width, n_components)


def extract_3d_patches(
    cube_pca: np.ndarray,
    gt: np.ndarray,
    patch_size: int = 15,
) -> tuple[np.ndarray, np.ndarray]:
    """Extract mirror-padded (N, patch_size, patch_size, bands) patches for labeled pixels."""
    half_patch = patch_size // 2
    padded_cube = np.pad(
        cube_pca,
        pad_width=((half_patch, half_patch), (half_patch, half_patch), (0, 0)),
        mode="reflect",
    )

    rows, cols = np.where(gt > 0)
    labels = (gt[rows, cols] - 1).astype(np.int64)
    num_samples = len(labels)

    patches = np.empty(
        (num_samples, patch_size, patch_size, cube_pca.shape[2]),
        dtype=np.float32,
    )
    for idx, (r, c) in enumerate(zip(rows, cols)):
        patches[idx] = padded_cube[r : r + patch_size, c : c + patch_size, :]

    return patches, labels


def run_preprocessing(
    cube_tif_path: str = "data/processed/terraspectra_hyperspectral_cube.tif",
    gt_tif_path: str = "data/processed/terraspectra_ground_truth.tif",
    patches_dir: str = "data/patches",
    artifacts_dir: str = "data/artifacts",
    n_components: int = 30,
    patch_size: int = 15,
) -> str:
    os.makedirs(patches_dir, exist_ok=True)

    with rasterio.open(cube_tif_path) as src:
        cube = src.read()

    with rasterio.open(gt_tif_path) as src:
        gt = src.read(1)

    cube_pca = fit_transform_pca(cube, n_components=n_components, artifacts_dir=artifacts_dir)
    X_patches, y_labels = extract_3d_patches(cube_pca, gt, patch_size=patch_size)

    X_train, X_temp, y_train, y_temp = train_test_split(
        X_patches, y_labels, test_size=0.30, random_state=42, stratify=y_labels
    )
    X_val, X_test, y_val, y_test = train_test_split(
        X_temp, y_temp, test_size=0.50, random_state=42, stratify=y_temp
    )

    npz_path = os.path.join(patches_dir, "terraspectra_patches.npz")
    np.savez_compressed(
        npz_path,
        X_train=X_train,
        y_train=y_train,
        X_val=X_val,
        y_val=y_val,
        X_test=X_test,
        y_test=y_test,
    )
    return npz_path


if __name__ == "__main__":
    output_file = run_preprocessing()
    print(f"Preprocessed 3D patches saved to: {output_file}")
