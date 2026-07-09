from app.llm import complete_json

SYSTEM = (
    "You are a concise travel concierge. You MUST only mention stays from the "
    "provided list, referenced by their id. Never invent a stay. "
    'Reply as JSON: {"pitch": str, "picks": [{"id": str, "why": str}]}.'
)


def _context(stays: list[dict]) -> str:
    lines = [
        f'- {s["id"]}: "{s["name"]}" ({s["kind"]}, ${s["price_per_night"]}/night, '
        f'rating {s["rating"]}, tags={s["tags"]})'
        for s in stays
    ]
    return "\n".join(lines)


def suggest(city: str, liked_tags: list[str], stays: list[dict]) -> dict:
    """A short personalized pitch over the *real* ranked stays — grounded."""
    user = (
        f"Traveler going to {city}. Their tastes: {', '.join(liked_tags) or 'none given'}.\n"
        f"Choose 3 stays from this list and explain each in one sentence:\n"
        f"{_context(stays)}"
    )
    return complete_json(SYSTEM, user)
