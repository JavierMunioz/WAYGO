from datetime import UTC, datetime
from typing import Annotated

from beanie import Document, Indexed
from pydantic import Field

from app.core.constants import PlaceCategory


class GeoPoint(dict):
    """GeoJSON Point wrapper stored as plain dict for MongoDB $geoNear queries."""

    @classmethod
    def create(cls, longitude: float, latitude: float) -> dict:
        return {"type": "Point", "coordinates": [longitude, latitude]}


class Place(Document):
    name: str
    slug: Annotated[str, Indexed(unique=True)]
    description: str
    country: Annotated[str, Indexed()]
    city: Annotated[str, Indexed()]
    category: Annotated[PlaceCategory, Indexed()]
    cover_image: str | None = None
    validation_radius: float = 30.0  # meters
    location: dict  # GeoJSON Point: {"type": "Point", "coordinates": [lng, lat]}

    # Denormalized counters
    total_visits: int = 0
    total_photos: int = 0
    total_likes: int = 0
    is_active: bool = True

    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    class Settings:
        name = "places"
        indexes = [
            [("location", "2dsphere")],
        ]
