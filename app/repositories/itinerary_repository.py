from app.models.itinerary import Itinerary
from app.repositories.base import BaseRepository


class ItineraryRepository(BaseRepository[Itinerary]):
    model = Itinerary

    async def get_by_trip_id(self, trip_id: str) -> Itinerary | None:
        return await Itinerary.find_one(Itinerary.trip_id == trip_id)
