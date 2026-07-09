from app.db import query


def fetch_candidates(city: str, max_price: float, limit: int = 500) -> list[dict]:
    """The rows worth ranking — the DB does the cheap, indexed, selective cut."""
    sql = """
        SELECT id, city, name, kind, price_per_night, rating, reviews,
               lat, lon, tags,
               EXTRACT(EPOCH FROM (now() - updated_at)) / 86400.0 AS days_old
        FROM listings
        WHERE city = %(city)s AND price_per_night <= %(max_price)s
        ORDER BY rating DESC, id ASC          -- deterministic tiebreak
        LIMIT %(limit)s
    """
    return query(sql, {"city": city, "max_price": max_price, "limit": limit})


def fetch_page(city: str, max_price: float, offset: int, limit: int) -> list[dict]:
    """A stable page of the catalog: deterministic order, then OFFSET/LIMIT."""
    sql = """
        SELECT id, city, name, kind, price_per_night, rating, lat, lon, tags
        FROM listings
        WHERE city = %(city)s AND price_per_night <= %(max_price)s
        ORDER BY rating DESC, id ASC          -- tiebreak by id → deterministic
        OFFSET %(offset)s LIMIT %(limit)s
    """
    return query(sql, {"city": city, "max_price": max_price,
                       "offset": offset, "limit": limit})


def search_listings(
    text: str, max_price: float, tags: list[str] | None = None, limit: int = 50
) -> list[dict]:
    """Full-text destination/stay search with optional tag facets."""
    sql = """
        SELECT id, city, name, kind, price_per_night, rating, lat, lon, tags,
               ts_rank(
                   to_tsvector('english', name || ' ' || description),
                   plainto_tsquery('english', %(text)s)
               ) AS text_rank
        FROM listings
        WHERE price_per_night <= %(max_price)s
          AND (%(text)s = '' OR
               to_tsvector('english', name || ' ' || description)
                   @@ plainto_tsquery('english', %(text)s))
          AND (%(tags)s::text[] IS NULL OR tags && %(tags)s::text[])
        ORDER BY text_rank DESC, rating DESC, id ASC
        LIMIT %(limit)s
    """
    return query(sql, {
        "text": text, "max_price": max_price,
        "tags": tags if tags else None, "limit": limit,
    })
