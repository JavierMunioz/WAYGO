from bson import ObjectId
from beanie.operators import Set

from app.core.constants import NotificationType
from app.models.notification import Notification
from app.repositories.base import BaseRepository


class NotificationRepository(BaseRepository[Notification]):
    model = Notification

    async def create_notification(
        self,
        user_id: str,
        notification_type: NotificationType,
        title: str,
        body: str,
        data: dict | None = None,
    ) -> Notification:
        notif = Notification(
            user_id=user_id,
            type=notification_type,
            title=title,
            body=body,
            data=data or {},
        )
        await notif.save()
        return notif

    async def get_user_notifications(
        self, user_id: str, unread_only: bool = False, skip: int = 0, limit: int = 20
    ) -> list[Notification]:
        query = {"user_id": user_id}
        if unread_only:
            query["read"] = False
        return (
            await Notification.find(query)
            .sort(-Notification.created_at)
            .skip(skip)
            .limit(limit)
            .to_list()
        )

    async def count_unread(self, user_id: str) -> int:
        return await Notification.find(Notification.user_id == user_id, Notification.read == False).count()

    async def mark_read(self, notification_id: str) -> None:
        await Notification.find_one(Notification.id == ObjectId(notification_id)).update(Set({"read": True}))

    async def mark_all_read(self, user_id: str) -> None:
        await Notification.find(Notification.user_id == user_id, Notification.read == False).update(
            Set({"read": True})
        )
