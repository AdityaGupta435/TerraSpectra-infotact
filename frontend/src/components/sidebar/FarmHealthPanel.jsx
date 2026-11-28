import React, { useState } from "react";
import { Sprout, BarChart3, Layers } from "lucide-react";
import HealthLegend from "./HealthLegend";
import PlotInspector from "./PlotInspector";
import AnalyticsPanel from "./AnalyticsPanel";
import { INITIAL_FARM_ANALYTICS } from "../../data/farmAnalyticsData";
import "../../styles/sidebar.css";

export default function FarmHealthPanel({
  summaryMetrics,
  selectedParcel,
  analyticsData = INITIAL_FARM_ANALYTICS,
}) {
  const [activeTab, setActiveTab] = useState("overview"); // "overview" | "analytics"

  return (
    <aside className="hud-sidebar">
      <div className="sidebar-blue-header">
        <Sprout size={19} color="#86efac" />
        <span>Farm Health & Analytics</span>
      </div>

      <div className="sidebar-tab-bar" role="tablist">
        <button
          type="button"
          role="tab"
          aria-selected={activeTab === "overview"}
          className={`sidebar-tab-btn ${activeTab === "overview" ? "active" : ""}`}
          onClick={() => setActiveTab("overview")}
        >
          <Layers size={14} />
          <span>Plot Overview</span>
        </button>
        <button
          type="button"
          role="tab"
          aria-selected={activeTab === "analytics"}
          className={`sidebar-tab-btn ${activeTab === "analytics" ? "active" : ""}`}
          onClick={() => setActiveTab("analytics")}
        >
          <BarChart3 size={14} />
          <span>Risk Analytics</span>
        </button>
      </div>

      <div className="sidebar-body">
        {activeTab === "overview" ? (
          <>
            <HealthLegend summaryMetrics={summaryMetrics} />
            <hr className="inspector-divider" />
            <PlotInspector parcel={selectedParcel} />
          </>
        ) : (
          <AnalyticsPanel analytics={analyticsData} />
        )}
      </div>
    </aside>
  );
}