import React from "react";
import { AlertTriangle, Map, Activity } from "lucide-react";
import SpectralAnomalyChart from "./SpectralAnomalyChart";

export default function AnalyticsPanel({ analytics }) {
  const atRiskPct = ((analytics.at_risk_hectares / analytics.total_hectares) * 100).toFixed(1);

  return (
    <div className="analytics-stack">
      {/* 1. Total Acreage at Risk KPI Row */}
      <div className="risk-kpi-grid">
        <div className="risk-kpi-card highlight-risk">
          <div className="risk-kpi-top">
            <AlertTriangle size={15} color="#dc2626" />
            <span className="risk-kpi-label">Acreage at Risk</span>
          </div>
          <span className="risk-kpi-value">{analytics.at_risk_hectares} ha</span>
          <span className="risk-kpi-sub">{atRiskPct}% of {analytics.total_hectares} ha</span>
        </div>

        <div className="risk-kpi-card">
          <div className="risk-kpi-top">
            <Activity size={15} color="#0b5ed7" />
            <span className="risk-kpi-label">Blight Risk Index</span>
          </div>
          <span className="risk-kpi-value">
            {(analytics.overall_blight_risk_score * 100).toFixed(0)}%
          </span>
          <span className="risk-kpi-sub">3D-CNN + ViT Mean</span>
        </div>
      </div>

      {/* 2. Disease Probability Breakdown by Crop */}
      <div className="breakdown-card">
        <div className="breakdown-header">
          <span className="section-heading">Disease Probability Breakdown</span>
        </div>

        <div className="crop-risk-list">
          {analytics.crop_breakdown.map((item) => {
            const probPct = Math.round(item.avg_stress_probability * 100);
            const barColor =
              probPct >= 70 ? "#dc2626" : probPct >= 40 ? "#eab308" : "#16a34a";

            return (
              <div className="crop-risk-row" key={item.crop_class}>
                <div className="crop-risk-top">
                  <span className="crop-name">
                    {item.crop_class} <span className="crop-ha">({item.hectares} ha)</span>
                  </span>
                  <span className="crop-prob" style={{ color: barColor }}>
                    {probPct}% risk
                  </span>
                </div>
                <div className="stacked-progress">
                  <div
                    className="seg-healthy"
                    style={{ width: `${item.healthy_pct}%` }}
                    title={`Healthy: ${item.healthy_pct}%`}
                  />
                  <div
                    className="seg-stress"
                    style={{ width: `${item.early_stress_pct}%` }}
                    title={`Early Stress: ${item.early_stress_pct}%`}
                  />
                  <div
                    className="seg-blight"
                    style={{ width: `${item.high_risk_pct}%` }}
                    title={`High Blight Risk: ${item.high_risk_pct}%`}
                  />
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* 3. Spectral Anomaly Chart */}
      <SpectralAnomalyChart anomalies={analytics.spectral_anomalies} />
    </div>
  );
}