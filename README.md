# TerraSpectra: Hyperspectral Crop Disease Forecasting

An end-to-end Geospatial Deep Learning and GIS Intelligence platform designed for early crop disease detection using 200+ band hyperspectral imagery, a Hybrid **3D-CNN + Vision Transformer (ViT)** architecture, **FastAPI** raster tiling inference, and a **React + Deck.gl** 3D visualization dashboard.

## Project Structure
- `ml_pipeline/`: Hyperspectral data preprocessing, PCA compression, and 3D-CNN + ViT training notebooks/scripts.
- `backend/`: FastAPI inference engine with sliding-window GeoTIFF raster tiling.
- `frontend/`: React + Deck.gl + Mapbox 3D GIS heatmap and analytics dashboard.
- `docs/`: Technical documentation, architecture diagrams, evaluation reports, and presentation.