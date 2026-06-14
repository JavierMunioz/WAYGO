from datetime import UTC, datetime

from beanie import Document, Indexed
from pydantic import Field
from typing import Annotated


class UserStats(Document):
    user_id: Annotated[str, Indexed(unique=True)]
    country: str | None = None
    city: str | None = None
    points: Annotated[int, Indexed()] = 0
    places_visited: int = 0
    badges: int = 0
    collections_completed: int = 0
    photos_uploaded: int = 0
    likes_received: int = 0
    followers: int = 0

    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    class Settings:
        name = "user_stats"
