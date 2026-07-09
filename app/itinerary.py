from app.llm import complete_json
from app.itinerary_schema import Itinerary
from app.suggestions import _context

SYSTEM = (
    "You are a travel planner. Build a day-by-day itinerary as JSON matching: "
    '{"city": str, "days": [{"day": int, "summary": str, '
    '"activities": [{"time": str, "title": str, "stay_id": str|null}]}]}. '
    "Any stay_id MUST be one of the provided stay ids — never invent one."
)


def generate_itinerary(
    city: str, days: int, liked_tags: list[str], stays: list[dict]
) -> Itinerary:
    """Generate, then *validate* the plan against the schema — a hard gate."""
    user = (
        f"Plan {days} days in {city} for a traveler who likes "
        f"{', '.join(liked_tags) or 'a bit of everything'}.\n"
        f"Available stays (use only these ids):\n{_context(stays)}"
    )
    raw = complete_json(SYSTEM, user)
    valid_ids = {s["id"] for s in stays}
    plan = Itinerary.model_validate(raw)        # raises on shape errors
    for day in plan.days:                       # ground-truth the stay ids
        for act in day.activities:
            if act.stay_id and act.stay_id not in valid_ids:
                act.stay_id = None              # drop hallucinated references
    return plan
