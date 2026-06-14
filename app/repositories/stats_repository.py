from beanie.operators import Inc, Set
from bson import ObjectId

from app.models.user_stats import UserStats
from app.repositories.base import BaseRepository


class StatsRepository(BaseRepository[UserStats]):
    model = UserStats

    async def get_by_user_id(self, user_id: str) -> UserStats | None:
        return await UserStats.find_one(UserStats.user_id == user_id)

    async def upsert(self, user_id: str, country: str | None = None, city: str | None = None) -> UserStats:
        stats = await self.get_by_user_id(user_id)
        if not stats:
            stats = UserStats(user_id=user_id, country=country, city=city)
            await stats.save()
        return stats

    async def increment(self, user_id: str, **fields: int) -> None:
        from datetime import UTC, datetime
        inc_payload = {k: v for k, v in fields.items()}
        await UserStats.find_one(UserStats.user_id == user_id).update(
            Inc(inc_payload),
            Set({"updated_at": datetime.now(UTC)}),
        )

    async def get_global_leaderboard(self, skip: int, limit: int) -> list[UserStats]:
        return await UserStats.find().sort(-UserStats.points).skip(skip).limit(limit).to_list()

    async def get_country_leaderboard(self, country: str, skip: int, limit: int) -> list[UserStats]:
        return (
            await UserStats.find(UserStats.country == country)
            .sort(-UserStats.points)
            .skip(skip)
            .limit(limit)
            .to_list()
        )

    async def get_city_leaderboard(self, city: str, skip: int, limit: int) -> list[UserStats]:
        return (
            await UserStats.find(UserStats.city == city)
            .sort(-UserStats.points)
            .skip(skip)
            .limit(limit)
            .to_list()
        )

    async def get_user_rank_global(self, user_id: str) -> int:
        user_stats = await self.get_by_user_id(user_id)
        if not user_stats:
            return 0
        return await UserStats.find(UserStats.points > user_stats.points).count() + 1
