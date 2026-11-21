# TerraSpectra — Mid-Project Review Summary (Days 1–10)

**Developer:** Aditya P. Gupta (`@AdityaGupta435`)  
**Repository:** `TerraSpectra-infotact`  
**Milestone:** Phase 1 & Phase 2 Complete (Data Engineering, 3D-CNN + ViT Architecture, Tuning, Explainability & Tensor Audit)

---

## 1. Executive Summary
TerraSpectra is an end-to-end hyperspectral agricultural stress & crop classification platform combining 3D spatial-spectral deep learning with interactive WebGL geospatial mapping. Across Days 1–10, the ingestion pipeline, 3D-CNN + Vision Transformer (ViT) fusion architecture, explainability suite, and 3D tensor memory audit were implemented and verified—surpassing the **90% accuracy benchmark** with **99.80% Overall Accuracy** on spatially augmented test data.

---

## 2. Phase-by-Phase Technical Accomplishments

### Phase 1: GIS & Hyperspectral Data Pipeline (Days 1–5)
* **Monorepo & Environment:** Configured Python (`uv`) backend + React/Vite/Deck.gl geospatial frontend.
* **Spatial Reprojection:** Converted raw 200-band Indian Pines hyperspectral datacube (`145×145×200`) into georeferenced `EPSG:4326` GeoTIFF format.
* **Dimensionality Reduction & Patching:** Reduced 200 spectral bands to **30 principal components** retaining **98.44% spectral variance** (`spectral_pca_30.joblib`), generating **10,249 labeled 3D patches (`15×15×30`)** split 70/15/15 (`7,174` train / `1,537` val / `1,538` test).
* **3D GIS Frontend Scaffold:** Built interactive Deck.gl + Mapbox viewport with modular telemetry controls.

### Phase 2: Hybrid 3D-CNN + ViT Deep Learning Model (Days 6–10)
* **Day 6 — 3D-CNN Backbone (`HybridSN`):** Built 3-layer 3D convolution + 2D spatial refinement baseline (`99.87%` test OA, `0.9985` Kappa).
* **Day 7 — Vision Transformer (ViT) Fusion (`Spectral3DViTFusion`):** Replaced 2D head with `9×9 = 81` spatial-spectral feature tokens, `[CLS]` token, learnable positional embeddings, and a 2-layer 4-head Self-Attention Transformer encoder (**379,248 parameters**, `1.5 MB` checkpoint, `99.93%` baseline OA)[cite: 1].
* **Day 8 — GPU Training & Regularization:** Trained on Colab T4 GPU for 60 epochs with random spatial flips, 90°/180°/270° rotations, label smoothing (`0.05`), and Cosine Annealing LR (`99.80%` test OA, `100.00%` val OA)[cite: 2].
* **Day 9 — Evaluation & Explainability:** Generated 16-class normalized confusion matrix (`99.65%` Average Accuracy, `99.38%` Macro F1) and extracted Multi-Head `[CLS]` attention maps + PC1–PC30 spectral attribution profiles[cite: 2].
* **Day 10 — 3D Tensor & Memory Audit:** Validated zero NaN/Inf activations and zero memory overflow across batch sizes `1` to `256` (`25,858.6 patches/sec` peak throughput, `0.4 MB` net RSS delta in `tensor_audit_day10.json`)[cite: 2].

---

## 3. Model Comparison & Benchmark Metrics

| Model Architecture | Parameters | Checkpoint Size | Test Overall Accuracy (OA) | Cohen's Kappa |
| :--- | :---: | :---: | :---: | :---: |
| **HybridSN (3D-2D CNN Baseline)** | ~1.20M | 4.6 MB | 99.87% | 0.9985 |
| **Spectral3DViTFusion (Baseline)** | 379,248 | 1.5 MB | 99.93% | 0.9993 |
| **Spectral3DViTFusion (Day 8 Tuned)** | **379,248** | **1.5 MB** | **99.80%** | **0.9978** |

---

## 4. Phase 3 Roadmap (Days 11–21)
* **Day 11:** Frontend Deck.gl `GridLayer` / `PolygonLayer` crop stress heatmap overlay (`Healthy`, `Early Stress`, `High Blight Risk`)[cite: 2].
* **Days 12–17:** FastAPI tiling inference engine connecting `spectral_scaler.joblib` + `spectral_pca_30.joblib` + `vit_fusion_tuned_day8.pth` to live map clicks and region scans[cite: 2].
* **Days 18–21:** End-to-end integration testing, containerization, and final deployment.
