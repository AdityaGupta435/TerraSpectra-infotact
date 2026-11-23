import React from "react";

export default function HealthLegend({ summaryMetrics }) {
  const tiers = [
    {
      title: "Healthy",
      subtitle: "Optimal chlorophyll & canopy vigor",
      color: "#16a34a",
      pct: summaryMetrics.healthy_pct,
    },
    {
      title: "Early Stress",
      subtitle: "Early water / nutrient deficiency",
      color: "#eab308",
      pct: summaryMetrics.early_stress_pct,
    },
    {
      title: "High Blight Risk",
      subtitle: "Critical spectral anomaly detected",
      color: "#dc2626",
      pct: summaryMetrics.high_risk_pct,
    },
  ];

  return (
    <div>
      {tiers.map((tier) => (
        <div className="legend-row" key={tier.title}>
          <div className="legend-left">
            <span className="legend-dot" style={{ background: tier.color }} />
            <div className="legend-text-group">
              <span className="legend-main">{tier.title}</span>
              <span className="legend-sub">{tier.subtitle}</span>
            </div>
          </div>
          <span className="legend-pct">{tier.pct}%</span>
        </div>
      ))}
    </div>
  );
}
