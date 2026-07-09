import { Stay } from "./api";

/** Plot stays as pins on a simple lat/lon projection. */
export function StayMap({ stays }: { stays: Stay[] }) {
  if (stays.length === 0) return null;
  const lats = stays.map((s) => s.lat);
  const lons = stays.map((s) => s.lon);
  const [minLat, maxLat] = [Math.min(...lats), Math.max(...lats)];
  const [minLon, maxLon] = [Math.min(...lons), Math.max(...lons)];

  const x = (lon: number) => ((lon - minLon) / (maxLon - minLon || 1)) * 100;
  const y = (lat: number) => (1 - (lat - minLat) / (maxLat - minLat || 1)) * 100;

  return (
    <div className="map" role="img" aria-label="Map of recommended stays">
      {stays.map((s) => (
        <span
          key={s.id}
          className="pin"
          style={{ left: `${x(s.lon)}%`, top: `${y(s.lat)}%` }}
          title={`${s.name} — $${s.price_per_night}/night`}
        />
      ))}
    </div>
  );
}
