import time

from app.itinerary import generate_itinerary
from app.itinerary_schema import Itinerary
from app.metrics import record_call


def generate_with_retry(
    city: str, days: int, liked_tags: list[str], stays: list[dict],
    attempts: int = 3,
) -> Itinerary:
    """Retry transient LLM failures with exponential backoff; record each call."""
    last_exc: Exception | None = None
    for attempt in range(attempts):
        started = time.monotonic()
        try:
            plan = generate_itinerary(city, days, liked_tags, stays)
            record_call(time.monotonic() - started, ok=True)
            return plan
        except Exception as exc:                # transient API error / bad JSON
            record_call(time.monotonic() - started, ok=False)
            last_exc = exc
            time.sleep(2 ** attempt * 0.5)      # 0.5s, 1s, 2s — exponential backoff
    raise RuntimeError(f"itinerary generation failed after {attempts} tries") from last_exc
