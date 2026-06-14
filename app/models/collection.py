from datetime import UTC, datetime

from beanie import Document, Indexed
from pydantic import Field
from typing import Annotated


class Collection(Document):
    name: str
    slug: Annotated[str, Indexed(unique=True)]
    description: str
    cover_image: str | None = None
    points: int = 50
    place_ids: list[str] = Field(default_factory=list)
    is_active: bool = True

    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    class Settings:
        name = "collections"


class UserCollectionProgress(Document):
    user_id: str
    collection_id: str
    visited_place_ids: list[str] = Field(default_factory=list)
    completed: bool = False
    completed_at: datetime | None = None
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    class Settings:
        name = "user_collection_progress"
