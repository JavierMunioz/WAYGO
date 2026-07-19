from datetime import UTC, datetime

from app.core.exceptions import ForbiddenError, ValidationError
from app.models.trip import Trip
from app.repositories.trip_repository import TripRepository
from app.schemas.trip import CreateTripRequest, UpdateTripRequest


class TripService:
    def __init__(self, trip_repo: TripRepository):
        self._repo = trip_repo

    async def create_trip(self, user_id: str, data: CreateTripRequest) -> Trip:
        trip = Trip(
            user_id=user_id,
            title=data.title,
            destination_country=data.destination_country,
            destination_city=data.destination_city,
            start_date=data.start_date,
            end_date=data.end_date,
            availability=data.availability,
            interests=data.interests,
            cover_image=data.cover_image,
        )
        await trip.save()
        return trip

    async def get_trip(self, trip_id: str, user_id: str) -> Trip:
        trip = await self._repo.get_by_id(trip_id)
        self._ensure_owner(trip, user_id)
        return trip

    async def list_user_trips(self, user_id: str, page: int, page_size: int) -> list[Trip]:
        from app.utils.pagination import compute_skip
        skip = compute_skip(page, page_size)
        return await self._repo.get_user_trips(user_id, skip=skip, limit=page_size)

    async def update_trip(self, trip_id: str, user_id: str, data: UpdateTripRequest) -> Trip:
        trip = await self._repo.get_by_id(trip_id)
        self._ensure_owner(trip, user_id)

        update_data = data.model_dump(exclude_none=True)
        for key, val in update_data.items():
            setattr(trip, key, val)

        # Mongo/Beanie devuelve datetimes naive (UTC); un PATCH parcial puede
        # dejar un campo aware (del request) junto a otro naive (de la DB).
        end_date = trip.end_date.replace(tzinfo=None) if trip.end_date.tzinfo else trip.end_date
        start_date = trip.start_date.replace(tzinfo=None) if trip.start_date.tzinfo else trip.start_date
        if end_date < start_date:
            raise ValidationError("end_date must be on or after start_date")

        trip.updated_at = datetime.now(UTC)
        await trip.save()
        return trip

    async def delete_trip(self, trip_id: str, user_id: str) -> None:
        trip = await self._repo.get_by_id(trip_id)
        self._ensure_owner(trip, user_id)
        await trip.delete()

    @staticmethod
    def _ensure_owner(trip: Trip, user_id: str) -> None:
        if trip.user_id != user_id:
            raise ForbiddenError("You do not own this trip")
