from bson import ObjectId

from app.models.visit import Visit
from app.repositories.base import BaseRepository


class VisitRepository(BaseRepository[Visit]):
    model = Visit

    async def get_by_user_and_place(self, user_id: str, place_id: str) -> Visit | None:
        return await Visit.find_one(Visit.user_id == user_id, Visit.place_id == place_id, Visit.verified == True)

    async def has_verified_visit(self, user_id: str, place_id: str) -> bool:
        return await self.get_by_user_and_place(user_id, place_id) is not None

    async def get_user_visits(self, user_id: str, skip: int = 0, limit: int = 20) -> list[Visit]:
        return (
            await Visit.find(Visit.user_id == user_id, Visit.verified == True)
            .sort(-Visit.created_at)
            .skip(skip)
            .limit(limit)
            .to_list()
        )

    async def get_user_visited_place_ids(self, user_id: str) -> list[str]:
        visits = await Visit.find(Visit.user_id == user_id, Visit.verified == True).to_list()
        return [v.place_id for v in visits]

    async def count_user_verified_visits(self, user_id: str) -> int:
        return await Visit.find(Visit.user_id == user_id, Visit.verified == True).count()

    async def get_place_visits(self, place_id: str, skip: int = 0, limit: int = 20) -> list[Visit]:
        return (
            await Visit.find(Visit.place_id == place_id, Visit.verified == True)
            .sort(-Visit.created_at)
            .skip(skip)
            .limit(limit)
            .to_list()
        )
