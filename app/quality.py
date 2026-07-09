from app.db import query


def recommendation_quality(window_hours: int = 24) -> dict:
    """Click-through and booking rates — is the ranker actually helping?"""
    sql = """
        SELECT
            COUNT(*) FILTER (WHERE action = 'view')  AS views,
            COUNT(*) FILTER (WHERE action = 'click') AS clicks,
            COUNT(*) FILTER (WHERE action = 'book')  AS books
        FROM interactions
        WHERE created_at > now() - make_interval(hours => %(h)s)
    """
    row = query(sql, {"h": window_hours})[0]
    views = row["views"] or 1
    return {
        "views": row["views"],
        "ctr": row["clicks"] / views,            # click-through rate
        "booking_rate": row["books"] / views,    # the rate that pays the bills
    }
