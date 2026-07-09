from app.repository import fetch_candidates
from app.personalization import affinity_tags
from app.scoring import score, Weights

DEFAULT_WEIGHTS = Weights()


def recommend(
    user_id: str,
    city: str,
    max_price: float,
    liked_tags: set[str],
    limit: int = 10,
) -> list[dict]:
    """fetch → score → sort → top-N, blending explicit + behavioral taste."""
    liked = liked_tags | affinity_tags(user_id)   # what they said ∪ what they did
    rows = fetch_candidates(city, max_price)
    scored = [
        {**row, "score": score(row, liked, max_price, DEFAULT_WEIGHTS)}
        for row in rows
    ]
    scored.sort(key=lambda r: r["score"], reverse=True)
    return scored[:limit]
