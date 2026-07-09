import math
from dataclasses import dataclass


@dataclass(frozen=True)
class Weights:
    rating: float = 1.0
    price: float = 0.6      # cheaper is better (we invert price)
    tag_match: float = 0.8
    recency: float = 0.4    # fresher listings get a gentle boost


def _price_feature(price: float, max_price: float) -> float:
    """Map price → 0..1 where cheaper is higher. Normalized so weights compare."""
    if max_price <= 0:
        return 0.0
    return max(0.0, 1.0 - price / max_price)


def _tag_feature(tags: list[str], liked: set[str]) -> float:
    """Fraction of the traveler's liked tags this listing satisfies (0..1)."""
    if not liked:
        return 0.0
    return len(set(tags) & liked) / len(liked)


def _recency_feature(days_old: float, half_life: float = 30.0) -> float:
    """Exponential decay: 1.0 at 0 days, 0.5 at one half-life, →0 as it ages."""
    if days_old < 0:
        return 1.0
    return math.exp(-math.log(2) * days_old / half_life)


def score(row: dict, liked: set[str], max_price: float, w: Weights) -> float:
    rating_feat = row["rating"] / 5.0               # 0..1
    price_feat = _price_feature(float(row["price_per_night"]), max_price)
    tag_feat = _tag_feature(row["tags"], liked)
    recency_feat = _recency_feature(float(row.get("days_old", 0.0)))
    return (
        w.rating * rating_feat
        + w.price * price_feat
        + w.tag_match * tag_feat
        + w.recency * recency_feat
    )
