from app.core.exceptions import AlreadyExistsError, ForbiddenError, NotFoundError
from app.models.user import User
from app.repositories.badge_repository import UserBadgeRepository
from app.repositories.collection_repository import UserCollectionProgressRepository
from app.repositories.follow_repository import FollowRepository
from app.repositories.stats_repository import StatsRepository
from app.repositories.user_repository import UserRepository
from app.schemas.user import UpdateProfileRequest, UserProfileResponse


class UserService:
    def __init__(
        self,
        user_repo: UserRepository,
        follow_repo: FollowRepository,
        user_badge_repo: UserBadgeRepository,
        collection_progress_repo: UserCollectionProgressRepository,
        stats_repo: StatsRepository,
    ):
        self._user_repo = user_repo
        self._follow_repo = follow_repo
        self._user_badge_repo = user_badge_repo
        self._collection_progress_repo = collection_progress_repo
        self._stats_repo = stats_repo

    async def get_profile(self, target_user_id: str, current_user_id: str | None = None) -> UserProfileResponse:
        user = await self._user_repo.get_by_id(target_user_id)
        rank = await self._stats_repo.get_user_rank_global(target_user_id)
        is_following = False
        if current_user_id and current_user_id != target_user_id:
            is_following = await self._follow_repo.is_following(current_user_id, target_user_id)

        return UserProfileResponse(
            id=str(user.id),
            username=user.username,
            avatar_url=user.avatar_url,
            bio=user.bio,
            country=user.country,
            city=user.city,
            followers_count=user.followers_count,
            following_count=user.following_count,
            places_visited_count=user.places_visited_count,
            photos_count=user.photos_count,
            badges_count=user.badges_count,
            likes_received_count=user.likes_received_count,
            points=user.points,
            created_at=user.created_at,
            is_following=is_following,
            rank_global=rank,
            is_superuser=user.is_superuser,
        )

    async def update_profile(self, user_id: str, data: UpdateProfileRequest) -> User:
        update_fields = data.model_dump(exclude_none=True)

        if "username" in update_fields:
            existing = await self._user_repo.get_by_username(update_fields["username"])
            if existing and str(existing.id) != user_id:
                raise AlreadyExistsError("Username already taken")

        return await self._user_repo.update_fields(user_id, **update_fields)

    async def get_user_badges(self, user_id: str):
        return await self._user_badge_repo.get_user_badges(user_id)

    async def get_user_collections(self, user_id: str):
        return await self._collection_progress_repo.get_all_user_progress(user_id)
