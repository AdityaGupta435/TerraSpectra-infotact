import React, { useState } from "react";
import "./styles/global.css";
import { FARM_VIEWPORT_CONFIG, INITIAL_FARM_TELEMETRY } from "./data/farmParcels";
import TopTelemetryBar from "./components/layout/TopTelemetryBar";
import FarmHealthPanel from "./components/sidebar/FarmHealthPanel";
import FarmMapViewport from "./components/map/FarmMapViewport";

export default function App() {
  const [viewState, setViewState] = useState(FARM_VIEWPORT_CONFIG.initialViewState);
  const [telemetry] = useState(INITIAL_FARM_TELEMETRY);
  const [selectedParcel, setSelectedParcel] = useState(
    INITIAL_FARM_TELEMETRY.parcels[0]
  );

  return (
    <div className="app-container">
      <TopTelemetryBar
        crs={FARM_VIEWPORT_CONFIG.crs}
        summaryMetrics={telemetry.summary_metrics}
      />

      <FarmHealthPanel
        summaryMetrics={telemetry.summary_metrics}
        selectedParcel={selectedParcel}
      />

      <FarmMapViewport
        viewState={viewState}
        onViewStateChange={setViewState}
        parcels={telemetry.parcels}
        gridPoints={telemetry.gridPoints}
        selectedParcelId={selectedParcel?.parcel_id}
        onSelectParcel={setSelectedParcel}
      />
    </div>
  );
}
