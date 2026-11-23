import React, { useMemo, useState } from "react";
import Map from "react-map-gl/maplibre";
import DeckGL from "@deck.gl/react";
import { PolygonLayer } from "@deck.gl/layers";
import { GridLayer } from "@deck.gl/aggregation-layers";
import "maplibre-gl/dist/maplibre-gl.css";
import {
  MAP_CONFIG,
  RISK_FILL_COLORS,
  GRID_HEATMAP_RANGE,
} from "../../constants/gisTheme";

export default function FarmMapViewport({
  viewState,
  onViewStateChange,
  parcels,
  gridPoints,
  selectedParcelId,
  onSelectParcel,
}) {
  const [layerMode, setLayerMode] = useState("combined"); // "combined" | "polygons" | "grid"

  const layers = useMemo(() => {
    const activeLayers = [];

    if (layerMode === "combined" || layerMode === "polygons") {
      activeLayers.push(
        new PolygonLayer({
          id: "terraspectra-parcel-polygons",
          data: parcels,
          pickable: true,
          stroked: true,
          filled: true,
          extruded: true,
          wireframe: false,
          lineWidthMinPixels: MAP_CONFIG.lineWidthMinPixels,
          getPolygon: (d) => d.polygon,
          getFillColor: (d) => {
            const base = RISK_FILL_COLORS[d.risk_tier] || [148, 163, 184, 210];
            // Slightly translucent fill in combined mode so GridLayer cells shine through
            return layerMode === "combined"
              ? [base[0], base[1], base[2], 125]
              : base;
          },
          getLineColor: (d) =>
            d.parcel_id === selectedParcelId ? [15, 23, 42, 255] : [255, 255, 255, 255],
          getElevation: (d) => d.elevation_meters || 60,
          elevationScale: layerMode === "combined" ? 0.6 : MAP_CONFIG.elevationScale,
          material: MAP_CONFIG.material,
          updateTriggers: {
            getLineColor: [selectedParcelId],
            getFillColor: [layerMode],
            elevationScale: [layerMode],
          },
          onHover: ({ object }) => {
            if (object) onSelectParcel(object);
          },
          onClick: ({ object }) => {
            if (object) onSelectParcel(object);
          },
        })
      );
    }

    if (layerMode === "combined" || layerMode === "grid") {
      activeLayers.push(
        new GridLayer({
          id: "terraspectra-stress-grid",
          data: gridPoints,
          pickable: true,
          extruded: true,
          cellSize: 115,
          elevationScale: 1.8,
          coverage: 0.86,
          colorRange: GRID_HEATMAP_RANGE,
          colorDomain: [0.05, 0.95],
          elevationDomain: [0.05, 0.95],
          getPosition: (d) => d.position,
          getColorWeight: (d) => d.stressScore,
          colorAggregation: "MEAN",
          getElevationWeight: (d) => d.stressScore,
          elevationAggregation: "MEAN",
          material: MAP_CONFIG.material,
          onClick: ({ object }) => {
            const sample = object?.points?.[0]?.source;
            if (sample) {
              const matched = parcels.find((p) => p.parcel_id === sample.parcel_id);
              if (matched) onSelectParcel(matched);
            }
          },
        })
      );
    }

    return activeLayers;
  }, [parcels, gridPoints, selectedParcelId, layerMode, onSelectParcel]);

  return (
    <div style={{ position: "relative", width: "100%", height: "100%" }}>
      <DeckGL
        viewState={viewState}
        onViewStateChange={({ viewState: next }) => onViewStateChange(next)}
        controller={true}
        layers={layers}
        getTooltip={({ object }) => {
          if (!object) return null;
          if (object.parcel_id) {
            return {
              text: `Plot ${object.parcel_id} (${object.crop_class})\nStatus: ${object.risk_tier} (${(
                object.stress_probability * 100
              ).toFixed(0)}% Risk)`,
            };
          }
          if (object.colorValue !== undefined) {
            return {
              text: `Spectral Grid Cell\nMean Blight/Stress Index: ${(object.colorValue * 100).toFixed(0)}%`,
            };
          }
          return null;
        }}
      >
      </DeckGL>

      <div className="map-layer-switcher" role="group" aria-label="Heatmap Layer Mode">
        {[
          { id: "combined", label: "Combined Heatmap" },
          { id: "polygons", label: "Field Polygons" },
          { id: "grid", label: "Spectral Grid" },
        ].map((mode) => (
          <button
            key={mode.id}
            type="button"
            className={`layer-pill-btn ${layerMode === mode.id ? "active" : ""}`}
            onClick={() => setLayerMode(mode.id)}
          >
            {mode.label}
          </button>
        ))}
      </div>
    </div>
  );
}
