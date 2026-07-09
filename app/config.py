import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    """Every runtime knob in one typed, immutable place — read from the env."""
    database_url: str = os.environ.get("DATABASE_URL", "postgresql://localhost/travel")
    redis_url: str = os.environ.get("REDIS_URL", "redis://localhost:6379")
    openai_api_key: str = os.environ.get("OPENAI_API_KEY", "")
    openai_model: str = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")
    pool_min: int = int(os.environ.get("DB_POOL_MIN", "1"))
    pool_max: int = int(os.environ.get("DB_POOL_MAX", "10"))
    profile_ttl_s: int = int(os.environ.get("PROFILE_TTL_S", "900"))


settings = Settings()
