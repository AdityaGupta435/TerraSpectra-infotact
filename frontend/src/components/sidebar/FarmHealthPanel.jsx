import React from "react";
import { Sprout } from "lucide-react";
import HealthLegend from "./HealthLegend";
import PlotInspector from "./PlotInspector";
import "../../styles/sidebar.css";

export default function FarmHealthPanel({ summaryMetrics, selectedParcel }) {
  return (
    <aside className="hud-sidebar">
      <div className="sidebar-blue-header">
        <Sprout size={19} color="#86efac" />
        <span>Farm Health Overview</span>
      </div>

      <div className="sidebar-body">
        <HealthLegend summaryMetrics={summaryMetrics} />
        <hr className="inspector-divider" />
        <PlotInspector parcel={selectedParcel} />
      </div>
    </aside>
  );
}
