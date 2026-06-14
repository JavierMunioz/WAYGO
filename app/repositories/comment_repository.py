from bson import ObjectId
from beanie.operators import Inc

from app.models.comment import Comment
from app.repositories.base import BaseRepository


class CommentRepository(BaseRepository[Comment]):
    model = Comment

    async def get_photo_comments(self, photo_id: str, skip: int = 0, limit: int = 20) -> list[Comment]:
        return (
            await Comment.find(Comment.photo_id == photo_id, Comment.is_active == True)
            .sort(Comment.created_at)
            .skip(skip)
            .limit(limit)
            .to_list()
        )

    async def count_photo_comments(self, photo_id: str) -> int:
        return await Comment.find(Comment.photo_id == photo_id, Comment.is_active == True).count()

    async def get_user_comments(self, user_id: str, skip: int = 0, limit: int = 20) -> list[Comment]:
        return (
            await Comment.find(Comment.user_id == user_id, Comment.is_active == True)
            .sort(-Comment.created_at)
            .skip(skip)
            .limit(limit)
            .to_list()
        )

    async def soft_delete(self, comment_id: str) -> None:
        from datetime import UTC, datetime
        from beanie.operators import Set
        await Comment.find_one(Comment.id == ObjectId(comment_id)).update(
            Set({"is_active": False, "updated_at": datetime.now(UTC)})
        )
