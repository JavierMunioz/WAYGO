from functools import lru_cache
from typing import Literal

from pydantic import AnyHttpUrl, MongoDsn, RedisDsn, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # App
    APP_NAME: str = "WAYGO"
    APP_VERSION: str = "1.0.0"
    APP_ENV: Literal["development", "staging", "production"] = "development"
    DEBUG: bool = False
    API_PREFIX: str = "/api/v1"
    ALLOWED_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:8080"]

    # MongoDB
    MONGODB_URI: str = "mongodb://localhost:27017"
    MONGODB_DB_NAME: str = "waygo"
    MONGODB_MIN_POOL_SIZE: int = 10
    MONGODB_MAX_POOL_SIZE: int = 100

    # Redis (leave empty to disable rate limiting)
    REDIS_URI: str = ""
    REDIS_CACHE_TTL: int = 300  # seconds

    # JWT
    JWT_SECRET_KEY: str = "change-me-in-production-use-256-bit-random-key"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 30

    # Email
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    EMAIL_FROM: str = "noreply@waygo.app"
    EMAIL_VERIFICATION_EXPIRE_HOURS: int = 24
    PASSWORD_RESET_EXPIRE_HOURS: int = 2

    # Storage (S3-compatible)
    STORAGE_PROVIDER: Literal["s3", "cloudflare_r2", "local"] = "local"
    STORAGE_BUCKET: str = "waygo-media"
    STORAGE_REGION: str = "us-east-1"
    STORAGE_ACCESS_KEY: str = ""
    STORAGE_SECRET_KEY: str = ""
    STORAGE_CDN_URL: str = "http://localhost:8000/media"
    LOCAL_MEDIA_PATH: str = "./media"

    # Rate Limiting
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_WINDOW_SECONDS: int = 60

    # Geo
    DEFAULT_VALIDATION_RADIUS_METERS: float = 30.0
    MAX_NEARBY_RADIUS_KM: float = 50.0

    # Points System
    POINTS_VISIT_PLACE: int = 10
    POINTS_UPLOAD_PHOTO: int = 5
    POINTS_RECEIVE_LIKE: int = 1
    POINTS_COMPLETE_COLLECTION: int = 50
    POINTS_EARN_BADGE: int = 100

    # Pagination
    DEFAULT_PAGE_SIZE: int = 20
    MAX_PAGE_SIZE: int = 100

    # Flights (Duffel API — https://duffel.com)
    DUFFEL_API_KEY: str = "YOUR_DUFFEL_ACCESS_TOKEN_HERE"
    DUFFEL_API_BASE_URL: str = "https://api.duffel.com"
    DUFFEL_VERSION: str = "v2"

    # Sentry
    SENTRY_DSN: str = ""

    @field_validator("ALLOWED_ORIGINS", mode="before")
    @classmethod
    def parse_origins(cls, v):
        if isinstance(v, list):
            return v
        if isinstance(v, str):
            v = v.strip()
            if not v:
                return ["http://localhost:3000", "http://localhost:8080"]
            # Accept both JSON array and comma-separated string
            import json as _json
            try:
                parsed = _json.loads(v)
                return parsed if isinstance(parsed, list) else [v]
            except _json.JSONDecodeError:
                return [o.strip() for o in v.split(",") if o.strip()]
        return v


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
