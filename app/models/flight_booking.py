from datetime import UTC, datetime
from typing import Annotated

from beanie import Document, Indexed
from pydantic import Field


class FlightBooking(Document):
    trip_id: Annotated[str, Indexed(unique=True)]
    user_id: Annotated[str, Indexed()]

    origin: str  # IATA code, e.g. "BAQ"
    destination: str  # IATA code, e.g. "BOG"
    departure_date: datetime
    return_date: datetime | None = None  # None for one-way — critical for Fase 3 lodging rule

    airline: str
    price: float
    currency: str
    booking_token: str  # Duffel offer id (off_...)
    deep_link: str | None = None  # reserved for a future affiliate/checkout flow

    # "held" = solo se guardó la oferta elegida (sin reservar de verdad);
    # "confirmed" = ya se creó la Order real en Duffel (/air/orders).
    status: str = "held"
    duffel_order_id: str | None = None
    booking_reference: str | None = None  # PNR de la aerolínea
    passenger_given_name: str | None = None
    passenger_family_name: str | None = None

    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    class Settings:
        name = "flight_bookings"
