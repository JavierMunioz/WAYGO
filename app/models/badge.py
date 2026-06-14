from datetime import UTC, datetime

from beanie import Document, Indexed
from pydantic import Field
from typing import Annotated

from app.core.constants import BadgeLevel


class Badge(Document):
    name: str
    slug: Annotated[str, Indexed(unique=True)]
    description: str
    image_url: str | None = None
    points: int = 100
    city: str | None = None
    country: str | None = None
    level: BadgeLevel = BadgeLevel.LEVEL_1
    is_active: bool = True

    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    class Settings:
        name = "badges"


class BadgeRequirement(Document):
    badge_id: str
    place_ids: list[str] = Field(default_factory=list)

    class Settings:
        name = "badge_requirements"


class UserBadge(Document):
    user_id: str
    badge_id: str
    obtained_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    class Settings:
        name = "user_badges"
