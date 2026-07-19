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

    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    class Settings:
        name = "lodging_bookings"
