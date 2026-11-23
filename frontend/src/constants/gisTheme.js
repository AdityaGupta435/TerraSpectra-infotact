export const MAP_CONFIG = {
  styleUrl: "https://basemaps.cartocdn.com/gl/positron-gl-style/style.json",
  elevationScale: 2.2,
  lineWidthMinPixels: 2.5,
  material: {
    ambient: 0.72,
    diffuse: 0.75,
    shininess: 32,
    specularColor: [255, 255, 255],
  },
};

export const RISK_FILL_COLORS = {
  Healthy: [22, 163, 74, 215],
  "Early Stress": [234, 179, 8, 220],
  "High Blight Risk": [220, 38, 38, 225],
};

export const RISK_BADGE_COLORS = {
  Healthy: "#16a34a",
  "Early Stress": "#eab308",
  "High Blight Risk": "#dc2626",
};

export const GRID_HEATMAP_RANGE = [
  [22, 163, 74, 190],    // Healthy (Green)
  [132, 204, 22, 200],   // Mild Transition
  [234, 179, 8, 215],    // Early Stress (Yellow)
  [249, 115, 22, 225],   // Elevated Stress
  [220, 38, 38, 235],    // High Blight Risk (Red)
];
