from datetime import datetime

from pydantic import Field

from app.schemas.common import BaseSchema


class LodgingSearchRequest(BaseSchema):
    destination_code: str = Field(min_length=2, max_length=10, description="Código de destino Hotelbeds, ej. PMI")
    check_in: datetime
    check_out: datetime
    adults: int = Field(default=2, ge=1, le=10)
    rooms: int = Field(default=1, ge=1, le=5)


class HotelOffer(BaseSchema):
    hotel_code: int
    hotel_name: str
    category_name: str
    destination_name: str
    latitude: float | None = None
    longitude: float | None = None
    price: float
    currency: str
    room_name: str
    board_name: str
    rate_key: str  # required to save the selected offer


class SaveLodgingRequest(BaseSchema):
    hotel_code: int
    hotel_name: str
    room_name: str
    board_name: str
    rate_key: str
    check_in: datetime
    check_out: datetime
    price: float = Field(gt=0)
    currency: str


class LodgingBookingResponse(BaseSchema):
    id: str
    trip_id: str
    hotel_code: int
    hotel_name: str
    room_name: str
    board_name: str
    check_in: datetime
    check_out: datetime
    price: float
    currency: str
    created_at: datetime
