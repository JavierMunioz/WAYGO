import logging
import time
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from app.core.config import settings
from app.core.exceptions import RateLimitError
from app.database.redis import CacheKeys, get_redis

logger = logging.getLogger("waygo.rate_limiter")

# Stricter limits for sensitive auth endpoints (requests, window_seconds)
_AUTH_STRICT_LIMITS: dict[str, tuple[int, int]] = {
    "/api/v1/auth/login": (10, 60),
    "/api/v1/auth/register": (5, 300),
    "/api/v1/auth/forgot-password": (5, 300),
    "/api/v1/auth/resend-verification": (5, 300),
    "/api/v1/auth/verify-email-otp": (10, 300),
    "/api/v1/auth/reset-password-otp": (10, 300),
    "/api/v1/auth/refresh": (20, 60),
}


async def _check_rate_limit(key: str, max_requests: int, window_seconds: int) -> None:
    redis = await get_redis()
    if redis is None:
        logger.warning("Redis unavailable — rate limiting skipped for key %s", key)
        return
    pipe = redis.pipeline()
    now = int(time.time())
    window_start = now - window_seconds

    await pipe.zremrangebyscore(key, 0, window_start)
    await pipe.zadd(key, {str(now): now})
    await pipe.zcard(key)
    await pipe.expire(key, window_seconds + 1)
    results = await pipe.execute()

    if results[2] > max_requests:
        raise RateLimitError(
            f"Rate limit exceeded: {max_requests} requests per {window_seconds}s"
        )


class RateLimiterMiddleware(BaseHTTPMiddleware):
    """Sliding-window rate limiter backed by Redis."""

    def __init__(self, app: ASGIApp):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        if request.url.path in ("/health", "/docs", "/openapi.json", "/redoc"):
            return await call_next(request)

        client_ip = request.client.host if request.client else "unknown"
        path = request.url.path

        try:
            # Apply stricter per-endpoint limits for auth routes first
            if path in _AUTH_STRICT_LIMITS:
                max_req, window = _AUTH_STRICT_LIMITS[path]
                await _check_rate_limit(
                    f"rl:auth:{path}:{client_ip}", max_req, window
                )

            # Global limit for all endpoints
            await _check_rate_limit(
                CacheKeys.rate_limit(client_ip),
                settings.RATE_LIMIT_REQUESTS,
                settings.RATE_LIMIT_WINDOW_SECONDS,
            )
        except RateLimitError:
            raise
        except Exception:
            logger.warning("Rate limiter error — failing open for IP %s", client_ip)

        response = await call_next(request)
        return response
