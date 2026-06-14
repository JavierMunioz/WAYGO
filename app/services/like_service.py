from app.core.exceptions import AlreadyExistsError, NotFoundError
from app.models.photo import PhotoLike
from app.repositories.photo_repository import PhotoLikeRepository, PhotoRepository
from app.repositories.place_repository import PlaceRepository
from app.repositories.user_repository import UserRepository
from app.services.notification_service import NotificationService
from app.services.points_service import PointsService


class LikeService:
    def __init__(
        self,
        like_repo: PhotoLikeRepository,
        photo_repo: PhotoRepository,
        user_repo: UserRepository,
        points_svc: PointsService,
        notification_svc: NotificationService,
        place_repo: PlaceRepository | None = None,
    ):
        self._like_repo = like_repo
        self._photo_repo = photo_repo
        self._user_repo = user_repo
        self._points_svc = points_svc
        self._notification_svc = notification_svc
        self._place_repo = place_repo

    async def like_photo(self, user_id: str, photo_id: str, liker_username: str) -> None:
        photo = await self._photo_repo.get_by_id(photo_id)
        if not photo.is_active:
            raise NotFoundError("Photo not found")

        if await self._like_repo.has_liked(user_id, photo_id):
            raise AlreadyExistsError("Already liked this photo")

        existing = await self._like_repo.get_like(user_id, photo_id)
        first_time = existing is None

        if existing:
            # Re-like after unlike: reactivate, never award points again
            existing.is_active = True
            await existing.save()
        else:
            await PhotoLike(user_id=user_id, photo_id=photo_id).save()

        await self._photo_repo.increment_likes(photo_id, 1)
        await self._user_repo.increment_counter(photo.user_id, "likes_received_count")
        if self._place_repo:
            await self._place_repo.increment_counter(photo.place_id, "total_likes")

        # Points and notification only on the very first like ever
        if first_time and photo.user_id != user_id:
            await self._points_svc.award_like_received(photo.user_id)
            await self._notification_svc.notify_photo_like(photo.user_id, liker_username, photo_id)

    async def unlike_photo(self, user_id: str, photo_id: str) -> None:
        like = await self._like_repo.get_like(user_id, photo_id)
        if not like or not like.is_active:
            raise NotFoundError("Like not found")

        # Soft delete: preserve the record so points are never re-awarded
        like.is_active = False
        await like.save()

        photo = await self._photo_repo.get_by_id(photo_id)
        await self._photo_repo.increment_likes(photo_id, -1)
        await self._user_repo.increment_counter(photo.user_id, "likes_received_count", amount=-1)
        if self._place_repo:
            await self._place_repo.increment_counter(photo.place_id, "total_likes", amount=-1)

    async def has_liked(self, user_id: str, photo_id: str) -> bool:
        return await self._like_repo.has_liked(user_id, photo_id)

    async def get_photo_likers(self, photo_id: str, page: int, page_size: int) -> list[PhotoLike]:
        from app.utils.pagination import compute_skip
        skip = compute_skip(page, page_size)
        return await self._like_repo.get_photo_likers(photo_id, skip=skip, limit=page_size)
