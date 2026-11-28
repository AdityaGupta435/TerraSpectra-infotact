import React from "react";

export default function SpectralAnomalyChart({ anomalies }) {
  const maxVal = 0.7;

  return (
    <div className="anomaly-chart-card">
      <div className="anomaly-header">
        <span className="section-heading">Spectral Anomaly Profile</span>
        <div className="chart-mini-legend">
          <span className="mini-legend-item">
            <span className="mini-dot" style={{ background: "#16a34a" }} />
            Healthy
          </span>
          <span className="mini-legend-item">
            <span className="mini-dot" style={{ background: "#dc2626" }} />
            Blight
          </span>
        </div>
      </div>

      <div className="anomaly-bars-list">
        {anomalies.map((band) => {
          const healthyWidth = Math.min(100, (band.healthy_reflectance / maxVal) * 100);
          const blightWidth = Math.min(100, (band.blight_reflectance / maxVal) * 100);
          const isPositive = band.deviation_pct > 0;

          return (
            <div className="anomaly-band-row" key={band.band_range_nm}>
              <div className="anomaly-band-meta">
                <div>
                  <span className="band-name">{band.short_label}</span>
                  <span className="band-range"> ({band.band_range_nm})</span>
                </div>
                <span
                  className={`deviation-pill ${isPositive ? "dev-up" : "dev-down"}`}
                >
                  {isPositive ? "+" : ""}
                  {band.deviation_pct}%
                </span>
              </div>

              <div className="dual-bar-track">
                <div className="bar-line">
                  <div
                    className="bar-fill healthy-bar"
                    style={{ width: `${healthyWidth}%` }}
                  />
                  <span className="bar-num">{band.healthy_reflectance.toFixed(2)}</span>
                </div>
                <div className="bar-line">
                  <div
                    className="bar-fill blight-bar"
                    style={{ width: `${blightWidth}%` }}
                  />
                  <span className="bar-num">{band.blight_reflectance.toFixed(2)}</span>
                </div>
              </div>
              <span className="band-component">{band.component}</span>
            </div>
          );
        })}
      </div>
    </div>
  );
}