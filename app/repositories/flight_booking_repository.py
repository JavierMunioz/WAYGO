from app.models.flight_booking import FlightBooking
from app.repositories.base import BaseRepository


class FlightBookingRepository(BaseRepository[FlightBooking]):
    model = FlightBooking

    async def get_by_trip_id(self, trip_id: str) -> FlightBooking | None:
        return await FlightBooking.find_one(FlightBooking.trip_id == trip_id)
