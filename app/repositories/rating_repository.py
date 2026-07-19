from app.models.rating import Rating
from app.repositories.base import BaseRepository


class RatingRepository(BaseRepository[Rating]):
    model = Rating

    async def get_by_user_and_place(self, user_id: str, place_id: str) -> Rating | None:
        return await Rating.find_one(Rating.user_id == user_id, Rating.place_id == place_id)

    async def get_place_ratings(self, place_id: str, skip: int = 0, limit: int = 20) -> list[Rating]:
        return (
            await Rating.find(Rating.place_id == place_id)
            .sort(-Rating.created_at)
            .skip(skip)
            .limit(limit)
            .to_list()
        )

    async def compute_average(self, place_id: str) -> tuple[float, int]:
        ratings = await Rating.find(Rating.place_id == place_id).to_list()
        if not ratings:
            return 0.0, 0
        avg = sum(r.score for r in ratings) / len(ratings)
        return round(avg, 2), len(ratings)
