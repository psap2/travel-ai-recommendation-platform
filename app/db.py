from psycopg_pool import ConnectionPool
from psycopg.rows import dict_row

from app.config import settings

# One pool for the whole process: connections are opened once and reused.
pool = ConnectionPool(
    settings.database_url,
    min_size=settings.pool_min,
    max_size=settings.pool_max,
    kwargs={"row_factory": dict_row},
    open=True,
)


def query(sql: str, params: dict | None = None) -> list[dict]:
    """Borrow a connection, run a read, return rows as dicts."""
    with pool.connection() as conn, conn.cursor() as cur:
        cur.execute(sql, params or {})
        return cur.fetchall()


def execute(sql: str, params_seq: list[tuple]) -> None:
    """Run a write (or batch of writes) inside one transaction."""
    with pool.connection() as conn, conn.cursor() as cur:
        for params in params_seq:
            cur.execute(sql, params)
        conn.commit()
