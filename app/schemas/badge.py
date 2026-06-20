from datetime import datetime

from pydantic import Field

from app.core.constants import BadgeLevel
from app.schemas.common import BaseSchema


class BadgeResponse(BaseSchema):
    id: str
    name: str
    slug: str
    description: str
    image_url: str | None = None
    points: int
    city: str | None = None
    country: str | None = None
    level: BadgeLevel


class UserBadgeResponse(BaseSchema):
    badge: BadgeResponse
    obtained_at: datetime


class BadgeWithProgressResponse(BadgeResponse):
    required_places: int
    visited_places: int
    progress_pct: float
    completed: bool


class CreateBadgeRequest(BaseSchema):
    name: str = Field(min_length=2, max_length=100)
    description: str = Field(min_length=10, max_length=500)
    image_url: str | None = None
    points: int = Field(default=100, ge=1, le=10000)
    city: str | None = None
    country: str | None = None
    level: BadgeLevel = BadgeLevel.LEVEL_1
    place_ids: list[str] = Field(default_factory=list)


class UpdateBadgeRequest(BaseSchema):
    name: str | None = Field(None, min_length=2, max_length=100)
    description: str | None = Field(None, min_length=10, max_length=500)
    image_url: str | None = None
    points: int | None = Field(None, ge=1, le=10000)
    city: str | None = None
    country: str | None = None
    level: BadgeLevel | None = None
    is_active: bool | None = None
    place_ids: list[str] | None = None


class BadgeRequirementResponse(BaseSchema):
    badge_id: str
    place_ids: list[str]


class BadgePlaceProgress(BaseSchema):
    place_id: str
    name: str
    city: str
    country: str
    slug: str
    cover_image: str | None = None
    visited: bool


class BadgeDetailResponse(BadgeWithProgressResponse):
    places: list[BadgePlaceProgress]
