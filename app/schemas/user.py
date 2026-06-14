from datetime import datetime

from pydantic import EmailStr, Field

from app.schemas.common import BaseSchema


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


class UserMiniResponse(BaseSchema):
    id: str
    username: str
    avatar_url: str | None = None
    points: int = 0
