from datetime import datetime

from pydantic import Field

from app.schemas.common import BaseSchema


class FlightSearchRequest(BaseSchema):
    origin: str = Field(min_length=3, max_length=3, description="Código IATA, ej. BAQ")
    destination: str = Field(min_length=3, max_length=3, description="Código IATA, ej. BOG")
    departure_date: datetime
    return_date: datetime | None = None
    adults: int = Field(default=1, ge=1, le=9)


class FlightOffer(BaseSchema):
    booking_token: str  # Duffel offer id (off_...) — expires after a couple of days
    airline: str
    price: float
    currency: str
    departure_time: datetime
    arrival_time: datetime
    return_departure_time: datetime | None = None
    return_arrival_time: datetime | None = None
    duration_minutes: int
    deep_link: str | None = None


class SaveFlightRequest(BaseSchema):
    booking_token: str
    origin: str = Field(min_length=3, max_length=3)
    destination: str = Field(min_length=3, max_length=3)
    departure_date: datetime
    return_date: datetime | None = None
    airline: str
    price: float = Field(gt=0)
    currency: str
    deep_link: str | None = None


class FlightBookingResponse(BaseSchema):
    id: str
    trip_id: str
    origin: str
    destination: str
    departure_date: datetime
    return_date: datetime | None = None
    airline: str
    price: float
    currency: str
    deep_link: str | None = None
    status: str
    booking_reference: str | None = None
    created_at: datetime


class ConfirmFlightBookingRequest(BaseSchema):
    given_name: str = Field(min_length=1, max_length=100)
    family_name: str = Field(min_length=1, max_length=100)
    born_on: str = Field(description="Fecha de nacimiento, formato YYYY-MM-DD")
    email: str
    phone_number: str = Field(description="Formato E.164, ej. +573001234567")
    title: str = Field(description="mr | mrs | ms | miss")
    gender: str = Field(description="m | f")
