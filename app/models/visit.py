from datetime import UTC, datetime

from beanie import Document
from pydantic import Field


class Visit(Document):
    user_id: str
    place_id: str
    latitude: float
    longitude: float
    distance: float  # calculated distance from place center in meters
    verified: bool = False

    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    class Settings:
        name = "visits"
