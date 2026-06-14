import logging

import redis.asyncio as aioredis
from redis.asyncio import Redis

from app.core.config import settings

logger = logging.getLogger(__name__)

_redis_client: Redis | None = None


async def get_redis() -> Redis | None:
    if not settings.REDIS_URI:
        return None
    global _redis_client
    if _redis_client is None:
        _redis_client = aioredis.from_url(
            settings.REDIS_URI,
            encoding="utf-8",
            decode_responses=True,
            socket_connect_timeout=5,
            socket_timeout=5,
            retry_on_timeout=True,
        )
    return _redis_client


async def close_redis() -> None:
    global _redis_client
    if _redis_client:
        await _redis_client.aclose()
        _redis_client = None
        logger.info("Redis connection closed.")


class CacheKeys:
    @staticmethod
    def user_profile(user_id: str) -> str:
        return f"profile:{user_id}"

    @staticmethod
    def place_detail(place_id: str) -> str:
        return f"place:{place_id}"

    @staticmethod
    def feed_recent(page: int) -> str:
        return f"feed:recent:{page}"

    @staticmethod
    def rankings_global(page: int) -> str:
        return f"rankings:global:{page}"

    @staticmethod
    def rankings_country(country: str, page: int) -> str:
        return f"rankings:country:{country}:{page}"

    @staticmethod
    def rankings_city(city: str, page: int) -> str:
        return f"rankings:city:{city}:{page}"

    @staticmethod
    def rate_limit(key: str) -> str:
        return f"ratelimit:{key}"

    @staticmethod
    def refresh_token_blacklist(jti: str) -> str:
        return f"token:blacklist:{jti}"

    @staticmethod
    def email_verification(token_jti: str) -> str:
        return f"email:verify:{token_jti}"

    @staticmethod
    def password_reset(token_jti: str) -> str:
        return f"pw:reset:{token_jti}"
