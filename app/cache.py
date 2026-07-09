import json

import redis

from app.config import settings

r = redis.Redis.from_url(settings.redis_url, decode_responses=True)


def get_json(key: str) -> dict | None:
    raw = r.get(key)
    return json.loads(raw) if raw else None


def set_json(key: str, value: dict, ttl_s: int) -> None:
    r.set(key, json.dumps(value), ex=ttl_s)
