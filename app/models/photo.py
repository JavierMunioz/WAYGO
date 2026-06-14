from datetime import UTC, datetime

from beanie import Document, Indexed
from pydantic import Field
from typing import Annotated


class Photo(Document):
    user_id: str
    place_id: str
    visit_id: str
    image_url: str
    caption: str | None = None
    likes_count: Annotated[int, Indexed()] = 0
    comments_count: int = 0
    is_active: bool = True

    created_at: Annotated[datetime, Indexed()] = Field(default_factory=lambda: datetime.now(UTC))

    class Settings:
        name = "photos"


class PhotoLike(Document):
    user_id: str
    photo_id: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    class Settings:
        name = "photo_likes"
