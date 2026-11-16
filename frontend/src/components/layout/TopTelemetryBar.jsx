import React from "react";
import { MapPin, Sprout, Droplets, Cpu } from "lucide-react";
import SatelliteLogo from "../common/SatelliteLogo";
import "../../styles/header.css";

export default function TopTelemetryBar({ crs, summaryMetrics }) {
  const kpiItems = [
    {
      label: "Farm Location",
      value: "79.1331° E, 21.1370° N",
      iconBg: "#e0f2fe",
      icon: <MapPin size={18} color="#0284c7" />,
    },
    {
      label: "Avg. Crop Greenery",
      value: `${summaryMetrics.mean_ndvi} NDVI`,
      iconBg: "#dcfce7",
      icon: <Sprout size={18} color="#16a34a" />,
    },
    {
      label: "Leaf Moisture Level",
      value: `${summaryMetrics.mean_ndwi} NDWI`,
      iconBg: "#e0f2fe",
      icon: <Droplets size={18} color="#0284c7" />,
    },
    {
      label: "AI Scan Engine",
      value: summaryMetrics.model_architecture,
      iconBg: "#eef2ff",
      icon: <Cpu size={18} color="#4338ca" />,
    },
  ];

  return (
    <header className="hud-header">
      <div className="brand-group">
        <SatelliteLogo />
        <span className="brand-title">TerraSpectra 3D</span>
        <span className="badge-crs">{crs}</span>
      </div>

      <div className="kpi-strip">
        {kpiItems.map((item) => (
          <div className="kpi-card" key={item.label}>
            <div className="kpi-icon-circle" style={{ background: item.iconBg }}>
              {item.icon}
            </div>
            <div className="kpi-text">
              <span className="kpi-label">{item.label}</span>
              <span className="kpi-value">{item.value}</span>
            </div>
          </div>
        ))}
      </div>
    </header>
  );
}
