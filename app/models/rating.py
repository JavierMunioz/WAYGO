from datetime import UTC, datetime
from typing import Annotated

from beanie import Document, Indexed
from pydantic import Field


class Rating(Document):
    user_id: Annotated[str, Indexed()]
    place_id: Annotated[str, Indexed()]
    score: int  # 1-5
    review: str | None = None

    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    class Settings:
        name = "ratings"
