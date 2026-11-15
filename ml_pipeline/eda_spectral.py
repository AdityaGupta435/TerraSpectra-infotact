"""
TerraSpectra — Deep Hyperspectral Exploratory Data Analysis & Stress Diagnostics
Computes class distributions, 200-band mean spectral reflectance curves,
NDVI/NDWI vegetation indices, 200x200 band correlation & PCA variance proof,
and Red-Edge 3-tier early crop stress segmentation.
"""

import os
import json
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from sklearn.decomposition import PCA
import rasterio

CLASS_NAMES = {
    1: "Alfalfa", 2: "Corn-notill", 3: "Corn-mintill", 4: "Corn",
    5: "Grass-pasture", 6: "Grass-trees", 7: "Grass-pasture-mowed",
    8: "Hay-windrowed", 9: "Oats", 10: "Soybean-notill",
    11: "Soybean-mintill", 12: "Soybean-clean", 13: "Wheat",
    14: "Woods", 15: "Buildings-Grass-Trees", 16: "Stone-Steel-Towers",
}


def compute_vegetation_indices(cube: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Compute NDVI, NDWI, and Red-Edge Chlorophyll Index from 200-band cube (Bands, H, W)."""
    red = cube[26]           # ~670 nm
    red_edge = cube[30]      # ~705 nm
    nir_shoulder = cube[36]  # ~780 nm
    nir = cube[38]           # ~800 nm
    swir = cube[119]         # ~1650 nm

    ndvi = (nir - red) / (nir + red + 1e-8)
    ndwi = (nir - swir) / (nir + swir + 1e-8)
    ci_rededge = (nir_shoulder / (red_edge + 1e-8)) - 1.0
    return ndvi, ndwi, ci_rededge


def run_eda(
    cube_tif_path: str = "data/processed/terraspectra_hyperspectral_cube.tif",
    gt_tif_path: str = "data/processed/terraspectra_ground_truth.tif",
    output_dir: str = "docs/eda_outputs",
) -> dict:
    os.makedirs(output_dir, exist_ok=True)

    with rasterio.open(cube_tif_path) as src:
        cube = src.read()

    with rasterio.open(gt_tif_path) as src:
        gt = src.read(1)

    ndvi, ndwi, ci_rededge = compute_vegetation_indices(cube)
    valid_mask = gt > 0
    ndvi_masked = np.where(valid_mask, ndvi, np.nan)
    ndwi_masked = np.where(valid_mask, ndwi, np.nan)
    wavelengths = np.linspace(400, 2500, cube.shape[0])

    # 1. Spectral Signatures Plot
    selected_classes = [2, 10, 11, 13, 14]
    plt.figure(figsize=(12, 5))
    for cls_id in selected_classes:
        mask = gt == cls_id
        mean_spectrum = cube[:, mask].mean(axis=1)
        std_spectrum = cube[:, mask].std(axis=1)
        plt.plot(wavelengths, mean_spectrum, label=f"{CLASS_NAMES[cls_id]} (n={mask.sum()})", linewidth=2)
        plt.fill_between(wavelengths, mean_spectrum - std_spectrum, mean_spectrum + std_spectrum, alpha=0.12)

    plt.axvspan(700, 1300, color="green", alpha=0.08, label="Red-Edge & NIR Chlorophyll Zone")
    plt.title("TerraSpectra EDA: Mean Hyperspectral Reflectance Signatures Across 200 Bands", fontweight="bold")
    plt.xlabel("Wavelength (nm)")
    plt.ylabel("Normalized Reflectance")
    plt.legend(loc="upper right")
    plt.grid(True, linestyle="--", alpha=0.4)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "eda_spectral_signatures.png"), dpi=200)
    plt.close()

    # 2. 3-Panel Spatial Vegetation Diagnostics
    fig, axes = plt.subplots(1, 3, figsize=(16, 4.8))
    im0 = axes[0].imshow(np.where(valid_mask, gt, np.nan), cmap="tab20")
    axes[0].set_title("Ground Truth Crop Parcels", fontweight="bold")
    plt.colorbar(im0, ax=axes[0], fraction=0.046, pad=0.04)

    im1 = axes[1].imshow(ndvi_masked, cmap="RdYlGn", vmin=-0.2, vmax=0.7)
    axes[1].set_title("NDVI (Chlorophyll Health Index)", fontweight="bold")
    plt.colorbar(im1, ax=axes[1], fraction=0.046, pad=0.04)

    im2 = axes[2].imshow(ndwi_masked, cmap="coolwarm_r", vmin=-0.5, vmax=0.5)
    axes[2].set_title("NDWI (Canopy Water / Early Stress)", fontweight="bold")
    plt.colorbar(im2, ax=axes[2], fraction=0.046, pad=0.04)

    plt.suptitle("TerraSpectra Spatial EDA: Vegetation & Early Stress Diagnostics", fontweight="bold")
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "eda_vegetation_indices.png"), dpi=200)
    plt.close()

    # 3. 200-Band Correlation & PCA Cumulative Variance Proof
    pixels_200 = cube.reshape(cube.shape[0], -1).T
    corr_matrix = np.corrcoef(pixels_200, rowvar=False)
    pca_full = PCA(n_components=50, random_state=42).fit(pixels_200)
    cum_variance = np.cumsum(pca_full.explained_variance_ratio_) * 100

    fig, axes = plt.subplots(1, 2, figsize=(15, 5.5))
    im = axes[0].imshow(corr_matrix, cmap="magma", vmin=0, vmax=1)
    axes[0].set_title("200-Band Spectral Correlation Matrix", fontweight="bold")
    plt.colorbar(im, ax=axes[0], fraction=0.046, pad=0.04)

    axes[1].plot(range(1, 51), cum_variance, marker="o", markersize=4, linewidth=2, color="#1f77b4")
    axes[1].axvline(30, color="red", linestyle="--", linewidth=1.8, label=f"30 PCs ({cum_variance[29]:.2f}% Var)")
    axes[1].axhline(99.0, color="green", linestyle=":", linewidth=1.5, label="99% Threshold")
    axes[1].set_title("PCA Cumulative Explained Variance (200 -> 30 Bands)", fontweight="bold")
    axes[1].legend(loc="lower right")
    axes[1].grid(True, linestyle="--", alpha=0.4)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "eda_band_correlation_pca.png"), dpi=200)
    plt.close()

    # 4. 3-Tier Early Stress Segmentation
    ci_valid = ci_rededge[valid_mask]
    q33, q66 = np.percentile(ci_valid, [33, 66])
    stress_map = np.zeros_like(gt, dtype=np.uint8)
    stress_map[valid_mask & (ci_rededge <= q33)] = 1
    stress_map[valid_mask & (ci_rededge > q33) & (ci_rededge <= q66)] = 2
    stress_map[valid_mask & (ci_rededge > q66)] = 3

    fig, axes = plt.subplots(1, 2, figsize=(15, 5.2))
    cmap_stress = ListedColormap(["#111827", "#ef4444", "#f59e0b", "#10b981"])
    im = axes[0].imshow(stress_map, cmap=cmap_stress, vmin=0, vmax=3)
    axes[0].set_title("Spatial Early Disease Risk Map (Red-Edge CI)", fontweight="bold")
    cbar = plt.colorbar(im, ax=axes[0], ticks=[0.375, 1.125, 1.875, 2.625], fraction=0.046, pad=0.04)
    cbar.ax.set_yticklabels(["Background", "High Risk", "Early Stress", "Healthy"])

    tier_labels = {
        1: "High Blight / Severe Stress Risk",
        2: "Pre-Visual Early Stress (Warning)",
        3: "Healthy High-Chlorophyll Canopy",
    }
    tier_colors = {1: "#ef4444", 2: "#f59e0b", 3: "#10b981"}
    for tier_id, label in tier_labels.items():
        mask = stress_map == tier_id
        axes[1].plot(wavelengths, cube[:, mask].mean(axis=1), label=label, color=tier_colors[tier_id], linewidth=2.2)

    axes[1].axvspan(680, 780, color="purple", alpha=0.1, label="Red-Edge Inflection Shift (680-780nm)")
    axes[1].set_title("Spectral Shift Across Crop Health Tiers (200 Bands)", fontweight="bold")
    axes[1].legend(loc="upper right")
    axes[1].grid(True, linestyle="--", alpha=0.4)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "eda_early_stress_tiers.png"), dpi=200)
    plt.close()

    summary = {
        "total_labeled_pixels": int(valid_mask.sum()),
        "num_classes": len(CLASS_NAMES),
        "ndvi_mean": round(float(np.nanmean(ndvi_masked)), 4),
        "ndwi_mean": round(float(np.nanmean(ndwi_masked)), 4),
        "pca_30_variance_pct": round(float(cum_variance[29]), 2),
        "high_risk_pixels": int((stress_map == 1).sum()),
        "early_stress_pixels": int((stress_map == 2).sum()),
        "healthy_pixels": int((stress_map == 3).sum()),
    }
    with open(os.path.join(output_dir, "eda_summary.json"), "w") as f:
        json.dump(summary, f, indent=2)

    return summary


if __name__ == "__main__":
    stats = run_eda()
    print("Deep EDA Completed:", stats)
