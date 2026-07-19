from datetime import UTC, datetime, timedelta

from app.core.exceptions import AlreadyExistsError, ForbiddenError, NotFoundError
from app.models.itinerary import Itinerary, ItineraryDay
from app.models.trip import Trip
from app.repositories.itinerary_repository import ItineraryRepository
from app.repositories.trip_repository import TripRepository
from app.schemas.itinerary import UpdateItineraryRequest


class ItineraryService:
    def __init__(self, itinerary_repo: ItineraryRepository, trip_repo: TripRepository):
        self._repo = itinerary_repo
        self._trip_repo = trip_repo

    async def generate_for_trip(self, trip_id: str, user_id: str) -> Itinerary:
        trip = await self._trip_repo.get_by_id(trip_id)
        self._ensure_owner(trip, user_id)

        existing = await self._repo.get_by_trip_id(trip_id)
        if existing:
            raise AlreadyExistsError("Itinerary already exists for this trip")

        days = [
            ItineraryDay(day_number=i + 1, date=trip.start_date + timedelta(days=i))
            for i in range(trip.days)
        ]
        itinerary = Itinerary(trip_id=trip_id, user_id=user_id, days=days)
        await itinerary.save()
        return itinerary

    async def get_by_trip(self, trip_id: str, user_id: str) -> Itinerary:
        trip = await self._trip_repo.get_by_id(trip_id)
        self._ensure_owner(trip, user_id)

        itinerary = await self._repo.get_by_trip_id(trip_id)
        if not itinerary:
            raise NotFoundError("Itinerary not found for this trip")
        return itinerary

    async def update_itinerary(self, trip_id: str, user_id: str, data: UpdateItineraryRequest) -> Itinerary:
        itinerary = await self.get_by_trip(trip_id, user_id)
        itinerary.days = [ItineraryDay(**d.model_dump()) for d in data.days]
        itinerary.updated_at = datetime.now(UTC)
        await itinerary.save()
        return itinerary

    async def delete_itinerary(self, trip_id: str, user_id: str) -> None:
        itinerary = await self.get_by_trip(trip_id, user_id)
        await itinerary.delete()

    @staticmethod
    def _ensure_owner(trip: Trip, user_id: str) -> None:
        if trip.user_id != user_id:
            raise ForbiddenError("You do not own this trip")
