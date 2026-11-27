/**
 * Day 14: GIS Coordinate Alignment Adapter
 * Validates EPSG:4326 [lon, lat] GeoJSON polygons from FastAPI (/predict-raster)
 * against Deck.gl farm viewport boundaries and builds aligned layer datasets.
 */

export function isPointWithinBounds([lon, lat], bounds, tolerance = 0.002) {
  return (
    Number.isFinite(lon) &&
    Number.isFinite(lat) &&
    lon >= bounds.west - tolerance &&
    lon <= bounds.east + tolerance &&
    lat >= bounds.south - tolerance &&
    lat <= bounds.north + tolerance
  );
}

export function adaptGeoJsonForDeckGL(geojson, farmBounds) {
  if (!geojson || geojson.type !== "FeatureCollection" || !Array.isArray(geojson.features)) {
    return { parcels: [], gridPoints: [], alignmentReport: { valid: 0, rejected: 0 } };
  }

  const parcels = [];
  const gridPoints = [];
  let rejected = 0;

  geojson.features.forEach((feature) => {
    const ring = feature?.geometry?.coordinates?.[0];
    const props = feature?.properties;

    if (!Array.isArray(ring) || ring.length < 4 || !props) {
      rejected += 1;
      return;
    }

    const allAligned = ring.every((coord) => isPointWithinBounds(coord, farmBounds));
    if (!allAligned) {
      rejected += 1;
      return;
    }

    parcels.push({
      ...props,
      polygon: ring,
    });

    // Compute tile centroid for Deck.gl GridLayer overlay
    const uniqueVertices = ring.slice(0, -1);
    const centerLon =
      uniqueVertices.reduce((sum, c) => sum + c[0], 0) / uniqueVertices.length;
    const centerLat =
      uniqueVertices.reduce((sum, c) => sum + c[1], 0) / uniqueVertices.length;

    gridPoints.push({
      position: [Number(centerLon.toFixed(6)), Number(centerLat.toFixed(6))],
      stressScore: props.stress_probability,
      parcel_id: props.parcel_id,
      crop_class: props.crop_class,
      risk_tier: props.risk_tier,
    });
  });

  return {
    parcels,
    gridPoints,
    alignmentReport: {
      valid: parcels.length,
      rejected,
      alignedPct:
        geojson.features.length > 0
          ? Number(((parcels.length / geojson.features.length) * 100).toFixed(1))
          : 0,
    },
  };
}