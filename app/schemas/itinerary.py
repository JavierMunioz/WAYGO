from datetime import datetime

from pydantic import Field

from app.schemas.common import BaseSchema


class ItineraryBlockSchema(BaseSchema):
    order: int
    start_time: str | None = None
    end_time: str | None = None
    place_id: str | None = None
    title: str = Field(min_length=1, max_length=200)
    notes: str | None = None
    is_free_time: bool = False


class ItineraryDaySchema(BaseSchema):
    day_number: int = Field(ge=1)
    date: datetime
    blocks: list[ItineraryBlockSchema] = Field(default_factory=list)


class UpdateItineraryRequest(BaseSchema):
    days: list[ItineraryDaySchema]


class ItineraryResponse(BaseSchema):
    id: str
    trip_id: str
    user_id: str
    days: list[ItineraryDaySchema]
    created_at: datetime
    updated_at: datetime
