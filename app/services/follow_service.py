from app.core.exceptions import AlreadyExistsError, ForbiddenError, NotFoundError
from app.models.follow import Follow
from app.repositories.follow_repository import FollowRepository
from app.repositories.user_repository import UserRepository
from app.services.notification_service import NotificationService


class FollowService:
    def __init__(
        self,
        follow_repo: FollowRepository,
        user_repo: UserRepository,
        notification_svc: NotificationService,
    ):
        self._follow_repo = follow_repo
        self._user_repo = user_repo
        self._notification_svc = notification_svc

    async def follow(self, follower_id: str, following_id: str, follower_username: str) -> None:
        if follower_id == following_id:
            raise ForbiddenError("Cannot follow yourself")

        target_user = await self._user_repo.get_by_id(following_id)

        if await self._follow_repo.is_following(follower_id, following_id):
            raise AlreadyExistsError("Already following this user")

        follow = Follow(follower_id=follower_id, following_id=following_id)
        await follow.save()

        await self._user_repo.increment_counter(follower_id, "following_count", 1)
        await self._user_repo.increment_counter(following_id, "followers_count", 1)

        await self._notification_svc.notify_new_follower(
            user_id=following_id,
            follower_username=follower_username,
            follower_id=follower_id,
        )

    async def unfollow(self, follower_id: str, following_id: str) -> None:
        follow = await self._follow_repo.get_follow(follower_id, following_id)
        if not follow:
            raise NotFoundError("Follow relationship not found")

        await follow.delete()
        await self._user_repo.increment_counter(follower_id, "following_count", -1)
        await self._user_repo.increment_counter(following_id, "followers_count", -1)

    async def is_following(self, follower_id: str, following_id: str) -> bool:
        return await self._follow_repo.is_following(follower_id, following_id)

    async def get_following_ids(self, user_id: str) -> list[str]:
        return await self._follow_repo.get_following_ids(user_id)

    async def get_followers(self, user_id: str, page: int, page_size: int):
        from app.utils.pagination import compute_skip
        skip = compute_skip(page, page_size)
        return await self._follow_repo.get_followers(user_id, skip=skip, limit=page_size)

    async def get_following(self, user_id: str, page: int, page_size: int):
        from app.utils.pagination import compute_skip
        skip = compute_skip(page, page_size)
        return await self._follow_repo.get_following(user_id, skip=skip, limit=page_size)
