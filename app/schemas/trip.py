from datetime import datetime

from pydantic import Field, model_validator

from app.core.constants import TripAvailability, TripStatus
from app.schemas.common import BaseSchema


class CreateTripRequest(BaseSchema):
    title: str = Field(min_length=2, max_length=200)
    destination_country: str
    destination_city: str
    start_date: datetime
    end_date: datetime
    availability: TripAvailability = TripAvailability.FULL_TIME
    interests: list[str] = Field(default_factory=list)
    cover_image: str | None = None

    @model_validator(mode="after")
    def validate_dates(self) -> "CreateTripRequest":
        if self.end_date < self.start_date:
            raise ValueError("end_date must be on or after start_date")
        return self


class UpdateTripRequest(BaseSchema):
    title: str | None = Field(None, min_length=2, max_length=200)
    start_date: datetime | None = None
    end_date: datetime | None = None
    availability: TripAvailability | None = None
    interests: list[str] | None = None
    status: TripStatus | None = None
    cover_image: str | None = None


class TripResponse(BaseSchema):
    id: str
    user_id: str
    title: str
    destination_country: str
    destination_city: str
    start_date: datetime
    end_date: datetime
    days: int
    availability: TripAvailability
    interests: list[str]
    status: TripStatus
    cover_image: str | None = None
    created_at: datetime
    updated_at: datetime
