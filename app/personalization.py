from app.db import query
from app.cache import get_json, set_json
from app.config import settings


def _build_profile(user_id: str) -> dict:
    """The user's revealed taste: tags from listings they clicked or booked."""
    sql = """
        SELECT DISTINCT unnest(l.tags) AS tag
        FROM interactions i
        JOIN listings l ON l.id = i.listing_id
        WHERE i.user_id = %(user_id)s AND i.action IN ('click', 'book')
        LIMIT 50
    """
    tags = [row["tag"] for row in query(sql, {"user_id": user_id})]
    return {"affinity_tags": tags}


def get_profile(user_id: str) -> dict:
    """Cache-aside: serve the cached profile or rebuild it from Postgres."""
    key = f"profile:{user_id}"
    cached = get_json(key)
    if cached is not None:
        return cached                         # cache hit — no DB round-trip
    profile = _build_profile(user_id)         # miss → compute…
    set_json(key, profile, settings.profile_ttl_s)  # …and cache for next time
    return profile


def affinity_tags(user_id: str) -> set[str]:
    return set(get_profile(user_id)["affinity_tags"])
