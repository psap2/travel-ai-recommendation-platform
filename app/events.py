from app.db import execute
from app.cache import r


def record_interaction(user_id: str, listing_ids: list[str], action: str) -> None:
    """Log what was shown/clicked/booked — the signal that improves ranking."""
    execute(
        "INSERT INTO interactions (user_id, listing_id, action) VALUES (%s, %s, %s)",
        [(user_id, lid, action) for lid in listing_ids],
    )
    # The user's taste just changed — drop their cached profile so it rebuilds.
    r.delete(f"profile:{user_id}")
