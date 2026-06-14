from datetime import UTC, datetime

from app.core.exceptions import ForbiddenError, NotFoundError
from app.models.comment import Comment
from app.repositories.comment_repository import CommentRepository
from app.repositories.photo_repository import PhotoRepository
from app.services.notification_service import NotificationService


class CommentService:
    def __init__(
        self,
        comment_repo: CommentRepository,
        photo_repo: PhotoRepository,
        notification_svc: NotificationService,
    ):
        self._comment_repo = comment_repo
        self._photo_repo = photo_repo
        self._notification_svc = notification_svc

    async def add_comment(self, user_id: str, photo_id: str, content: str, commenter_username: str) -> Comment:
        photo = await self._photo_repo.get_by_id(photo_id)
        if not photo.is_active:
            raise NotFoundError("Photo not found")

        comment = Comment(user_id=user_id, photo_id=photo_id, content=content)
        await comment.save()

        await self._photo_repo.increment_comments(photo_id, 1)

        if photo.user_id != user_id:
            await self._notification_svc.notify_comment(photo.user_id, commenter_username, photo_id)

        return comment

    async def update_comment(self, user_id: str, comment_id: str, content: str) -> Comment:
        comment = await self._comment_repo.get_by_id(comment_id)
        if comment.user_id != user_id:
            raise ForbiddenError("You can only edit your own comments")
        comment.content = content
        comment.updated_at = datetime.now(UTC)
        await comment.save()
        return comment

    async def delete_comment(self, user_id: str, comment_id: str, is_superuser: bool = False) -> None:
        comment = await self._comment_repo.get_by_id(comment_id)
        if comment.user_id != user_id and not is_superuser:
            # Also allow photo owner to delete comments on their photos
            photo = await self._photo_repo.get_by_id(comment.photo_id)
            if photo.user_id != user_id:
                raise ForbiddenError("Cannot delete this comment")

        await self._comment_repo.soft_delete(comment_id)
        await self._photo_repo.increment_comments(comment.photo_id, -1)

    async def get_photo_comments(self, photo_id: str, page: int, page_size: int) -> list[Comment]:
        from app.utils.pagination import compute_skip
        skip = compute_skip(page, page_size)
        return await self._comment_repo.get_photo_comments(photo_id, skip=skip, limit=page_size)
