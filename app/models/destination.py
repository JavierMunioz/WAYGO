from datetime import UTC, datetime
from typing import Annotated

from beanie import Document, Indexed
from pydantic import Field


class Destination(Document):
    name: str
    slug: Annotated[str, Indexed(unique=True)]
    country: Annotated[str, Indexed()]
    city: Annotated[str, Indexed()]
    description: str
    cover_image: str | None = None
    timezone: str | None = None
    currency: str | None = None
    is_active: bool = True

    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    class Settings:
        name = "destinations"
