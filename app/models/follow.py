from datetime import UTC, datetime

from beanie import Document
from pydantic import Field


class Follow(Document):
    follower_id: str
    following_id: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    class Settings:
        name = "follows"
