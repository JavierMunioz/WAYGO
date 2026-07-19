from datetime import UTC, datetime
from typing import Annotated

from beanie import Document, Indexed
from pydantic import BaseModel, Field


class ItineraryBlock(BaseModel):
    order: int
    start_time: str | None = None  # "09:00"
    end_time: str | None = None
    place_id: str | None = None
    title: str
    notes: str | None = None
    is_free_time: bool = False


class ItineraryDay(BaseModel):
    day_number: int
    date: datetime
    blocks: list[ItineraryBlock] = Field(default_factory=list)


class Itinerary(Document):
    trip_id: Annotated[str, Indexed(unique=True)]
    user_id: Annotated[str, Indexed()]
    days: list[ItineraryDay] = Field(default_factory=list)

    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    class Settings:
        name = "itineraries"
