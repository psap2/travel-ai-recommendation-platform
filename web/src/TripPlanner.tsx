import { useState } from "react";
import { planTrip, TripPlan } from "./api";
import { StayMap } from "./StayMap";

export function TripPlanner() {
  const [plan, setPlan] = useState<TripPlan | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function onPlan() {
    setLoading(true);
    setError(null);
    try {
      const result = await planTrip({
        user_id: "u1", query: "beach near old town", city: "Lisbon",
        days: 3, max_price: 250, liked_tags: ["beach", "wifi"],
      });
      setPlan(result);
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <main>
      <button onClick={onPlan} disabled={loading}>
        {loading ? "Planning…" : "Plan my trip"}
      </button>
      {error && <p className="error">{error}</p>}
      {plan && (
        <>
          <StayMap stays={plan.recommended_stays} />
          <ul className="stays">
            {plan.recommended_stays.map((s) => (
              <li key={s.id}>
                <strong>{s.name}</strong> · {s.kind} · ${s.price_per_night}/night
                · ★{s.rating.toFixed(1)}
              </li>
            ))}
          </ul>
          {plan.degraded ? (
            <p className="notice">Trip plan temporarily unavailable — retry.</p>
          ) : (
            plan.itinerary?.days.map((d) => (
              <section key={d.day}>
                <h3>Day {d.day}</h3>
                <p>{d.summary}</p>
              </section>
            ))
          )}
        </>
      )}
    </main>
  );
}
