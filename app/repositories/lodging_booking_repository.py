from app.models.lodging_booking import LodgingBooking
from app.repositories.base import BaseRepository


class LodgingBookingRepository(BaseRepository[LodgingBooking]):
    model = LodgingBooking

    async def get_by_trip_id(self, trip_id: str) -> LodgingBooking | None:
        return await LodgingBooking.find_one(LodgingBooking.trip_id == trip_id)
