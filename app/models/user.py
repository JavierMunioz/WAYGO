from datetime import UTC, datetime
from typing import Annotated

from beanie import Document, Indexed
from pydantic import EmailStr, Field


class User(Document):
    username: Annotated[str, Indexed(unique=True)]
    email: Annotated[EmailStr, Indexed(unique=True)]
    password_hash: str
    avatar_url: str | None = None
    bio: str | None = None
    country: str | None = None
    city: str | None = None
    preferred_currency: str = "USD"
    is_email_verified: bool = False
    is_active: bool = True
    is_superuser: bool = False

    # Denormalized counters (updated via atomic $inc for performance)
    followers_count: int = 0
    following_count: int = 0
    places_visited_count: int = 0
    photos_count: int = 0
    badges_count: int = 0
    likes_received_count: int = 0
    points: Annotated[int, Indexed()] = 0

    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    class Settings:
        name = "users"
        use_state_management = True


class RefreshToken(Document):
    user_id: str
    jti: str  # JWT ID — used for revocation
    expires_at: datetime

    class Settings:
        name = "refresh_tokens"
