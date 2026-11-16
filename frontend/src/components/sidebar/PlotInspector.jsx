import React from "react";
import { ShieldAlert, Leaf, Sprout, Droplets } from "lucide-react";
import { RISK_BADGE_COLORS } from "../../constants/gisTheme";

export default function PlotInspector({ parcel }) {
  if (!parcel) return null;

  const metrics = [
    {
      label: "Disease Risk",
      value: `${(parcel.stress_probability * 100).toFixed(0)}%`,
      icon: <ShieldAlert size={18} color="#2563eb" />,
    },
    {
      label: "Chlorophyll Score",
      value: parcel.red_edge_ci,
      icon: <Leaf size={18} color="#0284c7" />,
    },
    {
      label: "Crop Greenery",
      value: parcel.ndvi,
      icon: <Sprout size={18} color="#16a34a" />,
    },
    {
      label: "Moisture Level",
      value: parcel.ndwi,
      icon: <Droplets size={18} color="#0284c7" />,
    },
  ];

  return (
    <div>
      <div className="field-header-row">
        <div className="field-title-wrap">
          <span className="field-eyebrow">Selected Farm Plot (Hover or Click)</span>
          <span className="field-title">
            Plot {parcel.parcel_id} · {parcel.crop_class}
          </span>
        </div>
        <span
          className="status-pill"
          style={{ background: RISK_BADGE_COLORS[parcel.risk_tier] || "#16a34a" }}
        >
          {parcel.risk_tier}
        </span>
      </div>

      <div className="inspector-grid">
        {metrics.map((m) => (
          <div className="metric-box" key={m.label}>
            <div className="metric-icon-wrap">{m.icon}</div>
            <div className="metric-box-info">
              <span className="metric-box-label">{m.label}</span>
              <span className="metric-box-value">{m.value}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
