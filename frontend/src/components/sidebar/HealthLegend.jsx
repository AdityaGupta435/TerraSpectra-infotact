import React from "react";

export default function HealthLegend({ summaryMetrics }) {
  const tiers = [
    {
      title: "Healthy Crops",
      subtitle: "Strong growth & greenery",
      color: "#16a34a",
      pct: summaryMetrics.healthy_pct,
    },
    {
      title: "Early Stress Warning",
      subtitle: "Monitor water & nutrients",
      color: "#f59e0b",
      pct: summaryMetrics.early_stress_pct,
    },
    {
      title: "High Disease Risk",
      subtitle: "Immediate inspection needed",
      color: "#ef4444",
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
