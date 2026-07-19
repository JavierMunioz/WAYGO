from datetime import UTC, datetime
from typing import Annotated

from beanie import Document, Indexed
from pydantic import Field

from app.core.constants import TripAvailability, TripStatus


class Trip(Document):
    user_id: Annotated[str, Indexed()]
    title: str
    destination_country: str
    destination_city: str
    start_date: datetime
    end_date: datetime
    availability: TripAvailability = TripAvailability.FULL_TIME
    interests: list[str] = Field(default_factory=list)
    status: TripStatus = TripStatus.DRAFT
    cover_image: str | None = None

    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    class Settings:
        name = "trips"

    @property
    def days(self) -> int:
        return (self.end_date - self.start_date).days + 1
