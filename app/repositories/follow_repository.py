from app.models.follow import Follow
from app.repositories.base import BaseRepository


class FollowRepository(BaseRepository[Follow]):
    model = Follow

    async def get_follow(self, follower_id: str, following_id: str) -> Follow | None:
        return await Follow.find_one(
            Follow.follower_id == follower_id,
            Follow.following_id == following_id,
        )

    async def is_following(self, follower_id: str, following_id: str) -> bool:
        return await self.get_follow(follower_id, following_id) is not None

    async def get_followers(self, user_id: str, skip: int = 0, limit: int = 20) -> list[Follow]:
        return (
            await Follow.find(Follow.following_id == user_id)
            .sort(-Follow.created_at)
            .skip(skip)
            .limit(limit)
            .to_list()
        )

    async def get_following(self, user_id: str, skip: int = 0, limit: int = 20) -> list[Follow]:
        return (
            await Follow.find(Follow.follower_id == user_id)
            .sort(-Follow.created_at)
            .skip(skip)
            .limit(limit)
            .to_list()
        )

    async def get_following_ids(self, user_id: str) -> list[str]:
        follows = await Follow.find(Follow.follower_id == user_id).to_list()
        return [f.following_id for f in follows]

    async def count_followers(self, user_id: str) -> int:
        return await Follow.find(Follow.following_id == user_id).count()

    async def count_following(self, user_id: str) -> int:
        return await Follow.find(Follow.follower_id == user_id).count()
