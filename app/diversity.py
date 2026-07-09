def diversify(scored: list[dict], per_kind_cap: int = 2, limit: int = 10) -> list[dict]:
    """Walk best-first, but cap how many of each kind reach the final list."""
    seen_kind: dict[str, int] = {}
    out: list[dict] = []
    overflow: list[dict] = []
    for row in scored:                       # assumes already sorted best-first
        kind = row["kind"]
        if seen_kind.get(kind, 0) < per_kind_cap:
            out.append(row)
            seen_kind[kind] = seen_kind.get(kind, 0) + 1
        else:
            overflow.append(row)             # held back, used only to backfill
        if len(out) == limit:
            return out
    # If the cap left us short, backfill with the best held-back rows.
    return (out + overflow)[:limit]
