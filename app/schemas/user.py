from datetime import datetime
from urllib.parse import urlparse

from pydantic import EmailStr, Field, field_validator

from app.schemas.common import BaseSchema

_ALLOWED_AVATAR_SCHEMES = {"https"}
_ALLOWED_AVATAR_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".gif"}


def _validate_avatar_url(v: str | None) -> str | None:
    if v is None:
        return v
    parsed = urlparse(v)
    if parsed.scheme not in _ALLOWED_AVATAR_SCHEMES:
        raise ValueError("avatar_url must use HTTPS")
    path_lower = parsed.path.lower()
    if not any(path_lower.endswith(ext) for ext in _ALLOWED_AVATAR_EXTENSIONS):
        raise ValueError("avatar_url must point to an image file (jpg, png, webp, gif)")
    return v


class UserPublicResponse(BaseSchema):
    id: str
    username: str
    avatar_url: str | None = None
    bio: str | None = None
    country: str | None = None
    city: str | None = None
    followers_count: int
    following_count: int
    places_visited_count: int
    photos_count: int
    badges_count: int
    points: int
    created_at: datetime


class UserProfileResponse(UserPublicResponse):
    likes_received_count: int
    is_following: bool = False
    rank_global: int | None = None
    is_superuser: bool = False


class UpdateProfileRequest(BaseSchema):
    username: str | None = Field(None, min_length=3, max_length=30, pattern=r"^[a-zA-Z0-9_]+$")
    bio: str | None = Field(None, max_length=300)
    country: str | None = None
    city: str | None = None
    avatar_url: str | None = None

    @field_validator("avatar_url")
    @classmethod
    def validate_avatar_url(cls, v: str | None) -> str | None:
        return _validate_avatar_url(v)


class UserMiniResponse(BaseSchema):
    id: str
    username: str
    avatar_url: str | None = None
    points: int = 0
