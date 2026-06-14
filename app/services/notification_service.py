from app.core.constants import NotificationType
from app.repositories.notification_repository import NotificationRepository


class NotificationService:
    def __init__(self, notification_repo: NotificationRepository):
        self._repo = notification_repo

    async def notify_new_badge(self, user_id: str, badge_name: str, badge_id: str) -> None:
        await self._repo.create_notification(
            user_id=user_id,
            notification_type=NotificationType.NEW_BADGE,
            title="Nueva medalla obtenida",
            body=f"Has ganado la medalla: {badge_name}",
            data={"badge_id": badge_id},
        )

    async def notify_collection_completed(self, user_id: str, collection_name: str, collection_id: str) -> None:
        await self._repo.create_notification(
            user_id=user_id,
            notification_type=NotificationType.COLLECTION_COMPLETED,
            title="Colección completada",
            body=f"Completaste la colección: {collection_name}",
            data={"collection_id": collection_id},
        )

    async def notify_photo_like(self, user_id: str, liker_username: str, photo_id: str) -> None:
        await self._repo.create_notification(
            user_id=user_id,
            notification_type=NotificationType.PHOTO_LIKE,
            title="Le gustó tu foto",
            body=f"A {liker_username} le gustó tu foto",
            data={"photo_id": photo_id},
        )

    async def notify_new_follower(self, user_id: str, follower_username: str, follower_id: str) -> None:
        await self._repo.create_notification(
            user_id=user_id,
            notification_type=NotificationType.NEW_FOLLOWER,
            title="Nuevo seguidor",
            body=f"{follower_username} ahora te sigue",
            data={"follower_id": follower_id},
        )

    async def notify_comment(self, user_id: str, commenter_username: str, photo_id: str) -> None:
        await self._repo.create_notification(
            user_id=user_id,
            notification_type=NotificationType.COMMENT,
            title="Nuevo comentario",
            body=f"{commenter_username} comentó tu foto",
            data={"photo_id": photo_id},
        )

    async def get_user_notifications(self, user_id: str, unread_only: bool, page: int, page_size: int):
        from app.utils.pagination import compute_skip
        skip = compute_skip(page, page_size)
        notifications = await self._repo.get_user_notifications(
            user_id=user_id, unread_only=unread_only, skip=skip, limit=page_size
        )
        unread_count = await self._repo.count_unread(user_id)
        return notifications, unread_count

    async def mark_read(self, notification_id: str) -> None:
        await self._repo.mark_read(notification_id)

    async def mark_all_read(self, user_id: str) -> None:
        await self._repo.mark_all_read(user_id)
