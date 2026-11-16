import React, { useMemo } from "react";
import Map from "react-map-gl/maplibre";
import DeckGL from "@deck.gl/react";
import { GeoJsonLayer } from "@deck.gl/layers";
import "maplibre-gl/dist/maplibre-gl.css";
import { MAP_CONFIG, RISK_FILL_COLORS } from "../../constants/gisTheme";

export default function FarmMapViewport({
  viewState,
  onViewStateChange,
  geojsonData,
  onSelectParcel,
}) {
  const layers = useMemo(() => {
    return [
      new GeoJsonLayer({
        id: "terraspectra-farm-parcels",
        data: geojsonData,
        pickable: true,
        stroked: true,
        filled: true,
        extruded: true,
        wireframe: false,
        lineWidthMinPixels: MAP_CONFIG.lineWidthMinPixels,
        getFillColor: (feature) =>
          RISK_FILL_COLORS[feature.properties.risk_tier] || [148, 163, 184, 230],
        getLineColor: [255, 255, 255, 255],
        getElevation: (feature) => feature.properties.elevation_meters || 60,
        elevationScale: MAP_CONFIG.elevationScale,
        material: MAP_CONFIG.material,
        onHover: ({ object }) => {
          if (object) onSelectParcel(object.properties);
        },
        onClick: ({ object }) => {
          if (object) onSelectParcel(object.properties);
        },
      }),
    ];
  }, [geojsonData, onSelectParcel]);

  return (
    <DeckGL
      viewState={viewState}
      onViewStateChange={({ viewState: next }) => onViewStateChange(next)}
      controller={true}
      layers={layers}
    >
    </DeckGL>
  );
}
