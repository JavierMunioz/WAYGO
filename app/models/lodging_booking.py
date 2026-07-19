from datetime import UTC, datetime
from typing import Annotated

from beanie import Document, Indexed
from pydantic import Field


class LodgingBooking(Document):
    trip_id: Annotated[str, Indexed(unique=True)]
    user_id: Annotated[str, Indexed()]

    hotel_code: int
    hotel_name: str
    room_name: str
    board_name: str
    rate_key: str  # Hotelbeds rate key (needed to complete a real booking later)

    check_in: datetime
    check_out: datetime

    price: float
    currency: str

    # "held" = solo guardada localmente (tarifa verificada, sin reservar de
    # verdad); "confirmed" = ya se llamó a Hotelbeds /bookings y hay una
    # reserva real con ese hotel.
    status: str = "held"
    hotelbeds_reference: str | None = None  # locator que devuelve Hotelbeds al confirmar
    holder_name: str | None = None
    holder_surname: str | None = None

    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    class Settings:
        name = "lodging_bookings"
