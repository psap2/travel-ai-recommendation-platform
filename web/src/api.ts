export interface Stay {
  id: string;
  name: string;
  kind: string;
  price_per_night: number;
  rating: number;
  lat: number;
  lon: number;
  tags: string[];
  score?: number;
}

export interface TripPlan {
  discovery: Stay[];
  recommended_stays: Stay[];
  suggestion: { pitch: string; picks: { id: string; why: string }[] };
  itinerary: {
    city: string;
    days: { day: number; summary: string;
            activities: { time: string; title: string; stay_id: string | null }[] }[];
  } | null;
  degraded: boolean;
}

export async function planTrip(req: {
  user_id: string; query: string; city: string;
  days: number; max_price: number; liked_tags: string[];
}): Promise<TripPlan> {
  const res = await fetch("/api/trips/plan", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(req),
  });
  if (!res.ok) throw new Error(`plan failed: ${res.status}`);
  return res.json();
}
