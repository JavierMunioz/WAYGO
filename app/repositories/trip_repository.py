from app.models.trip import Trip
from app.repositories.base import BaseRepository


class TripRepository(BaseRepository[Trip]):
    model = Trip

    async def get_user_trips(self, user_id: str, skip: int = 0, limit: int = 20) -> list[Trip]:
        return (
            await Trip.find(Trip.user_id == user_id)
            .sort(-Trip.created_at)
            .skip(skip)
            .limit(limit)
            .to_list()
        )

    async def count_user_trips(self, user_id: str) -> int:
        return await Trip.find(Trip.user_id == user_id).count()
