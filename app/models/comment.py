from datetime import UTC, datetime

from beanie import Document, Indexed
from pydantic import Field
from typing import Annotated


class Comment(Document):
    user_id: str
    photo_id: Annotated[str, Indexed()]
    content: str
    is_active: bool = True

    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    class Settings:
        name = "comments"
