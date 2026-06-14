import logging
import logging.config
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.exceptions import WaygoException
from app.database.mongodb import close_mongo_connection, connect_to_mongo
from app.database.redis import close_redis
from app.middleware.logging_middleware import LoggingMiddleware
from app.middleware.rate_limiter import RateLimiterMiddleware

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {"format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s"},
    },
    "handlers": {
        "console": {"class": "logging.StreamHandler", "formatter": "default"},
    },
    "root": {"handlers": ["console"], "level": "INFO"},
    "loggers": {
        "waygo": {"level": "DEBUG" if settings.DEBUG else "INFO", "propagate": True},
        "motor": {"level": "WARNING", "propagate": True},
    },
}
logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting WAYGO API v%s [%s]", settings.APP_VERSION, settings.APP_ENV)
    await connect_to_mongo()
    yield
    await close_mongo_connection()
    await close_redis()
    logger.info("WAYGO API shutdown complete.")


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description="WAYGO — Geo-verified social tourism platform",
        docs_url="/docs" if settings.APP_ENV != "production" else None,
        redoc_url="/redoc" if settings.APP_ENV != "production" else None,
        lifespan=lifespan,
    )

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Custom middleware (order matters — outermost first)
    app.add_middleware(LoggingMiddleware)
    app.add_middleware(RateLimiterMiddleware)

    # Global exception handler
    @app.exception_handler(WaygoException)
    async def waygo_exception_handler(request: Request, exc: WaygoException) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail},
        )

    # Health check (no auth, no rate limit)
    @app.get("/health", include_in_schema=False)
    async def health():
        return {"status": "ok", "version": settings.APP_VERSION}

    # API routes
    app.include_router(api_router, prefix=settings.API_PREFIX)

    # Serve uploaded media files (local storage mode only)
    if settings.STORAGE_PROVIDER == "local":
        media_path = Path(settings.LOCAL_MEDIA_PATH)
        media_path.mkdir(parents=True, exist_ok=True)
        app.mount("/media", StaticFiles(directory=str(media_path)), name="media")

    return app


app = create_app()
