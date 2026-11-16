export const MAP_CONFIG = {
  styleUrl: "https://basemaps.cartocdn.com/gl/positron-nolabels-gl-style/style.json",
  elevationScale: 2.3,
  lineWidthMinPixels: 2.5,
  material: {
    ambient: 0.68,
    diffuse: 0.72,
    shininess: 32,
    specularColor: [255, 255, 255],
  },
};

export const RISK_FILL_COLORS = {
  Healthy: [22, 163, 74, 245],
  "Early Stress": [245, 158, 11, 245],
  "High Risk": [239, 68, 68, 245],
};

export const RISK_BADGE_COLORS = {
  Healthy: "#16a34a",
  "Early Stress": "#d97706",
  "High Risk": "#dc2626",
};
