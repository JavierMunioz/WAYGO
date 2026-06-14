import time
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from app.core.config import settings
from app.core.exceptions import RateLimitError
from app.database.redis import CacheKeys, get_redis


class RateLimiterMiddleware(BaseHTTPMiddleware):
    """Sliding-window rate limiter backed by Redis."""

    def __init__(self, app: ASGIApp):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Skip rate limiting for health checks
        if request.url.path in ("/health", "/docs", "/openapi.json", "/redoc"):
            return await call_next(request)

        client_ip = request.client.host if request.client else "unknown"
        key = CacheKeys.rate_limit(client_ip)

        try:
            redis = await get_redis()
            if redis is None:
                return await call_next(request)
            pipe = redis.pipeline()
            now = int(time.time())
            window_start = now - settings.RATE_LIMIT_WINDOW_SECONDS

            await pipe.zremrangebyscore(key, 0, window_start)
            await pipe.zadd(key, {str(now): now})
            await pipe.zcard(key)
            await pipe.expire(key, settings.RATE_LIMIT_WINDOW_SECONDS + 1)
            results = await pipe.execute()

            request_count = results[2]
            if request_count > settings.RATE_LIMIT_REQUESTS:
                raise RateLimitError(
                    f"Rate limit exceeded: {settings.RATE_LIMIT_REQUESTS} requests per {settings.RATE_LIMIT_WINDOW_SECONDS}s"
                )
        except RateLimitError:
            raise
        except Exception:
            # Redis unavailable — fail open
            pass

        response = await call_next(request)
        return response
