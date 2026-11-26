from __future__ import annotations

from typing import Any, Dict, List
from pydantic import BaseModel, Field


class SummaryMetrics(BaseModel):
    total_hectares: float
    healthy_pct: float
    early_stress_pct: float
    high_risk_pct: float
    mean_ndvi: float
    mean_ndwi: float
    model_architecture: str


class TilingConfig(BaseModel):
    patch_size: int
    stride: int
    overlap_pixels: int
    total_tiles: int
    stitched_coverage_pct: float
    inference_backend: str


class GeoJSONFeatureCollection(BaseModel):
    type: str = "FeatureCollection"
    features: List[Dict[str, Any]]


class PredictRasterResponse(BaseModel):
    scan_id: str
    crs: str
    raster_shape: Dict[str, int]
    tiling_config: TilingConfig
    summary_metrics: SummaryMetrics
    geojson: GeoJSONFeatureCollection


class CropRiskBreakdown(BaseModel):
    crop_class: str
    hectares: float
    healthy_pct: float
    early_stress_pct: float
    high_risk_pct: float
    avg_stress_probability: float


class SpectralBandAnomaly(BaseModel):
    band_range_nm: str
    component: str
    healthy_reflectance: float
    blight_reflectance: float
    deviation_pct: float


class FarmAnalyticsResponse(BaseModel):
    scan_id: str
    total_hectares: float
    at_risk_hectares: float
    overall_blight_risk_score: float
    summary_metrics: SummaryMetrics
    crop_breakdown: List[CropRiskBreakdown]
    spectral_anomalies: List[SpectralBandAnomaly]


class WeeklyTrendPoint(BaseModel):
    week_offset: int = Field(..., description="-3 to 0 (Week 0 = Current Scan)")
    label: str
    date_label: str
    healthy_pct: float
    early_stress_pct: float
    high_risk_pct: float
    mean_ndvi: float
    mean_ndwi: float
    blight_index: float
    advisory_note: str


class HistoricalTrendResponse(BaseModel):
    scan_id: str
    location: str
    timeline: List[WeeklyTrendPoint]