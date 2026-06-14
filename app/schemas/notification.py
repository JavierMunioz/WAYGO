from datetime import datetime

from app.core.constants import NotificationType
from app.schemas.common import BaseSchema


class NotificationResponse(BaseSchema):
    id: str
    type: NotificationType
    title: str
    body: str
    data: dict
    read: bool
    created_at: datetime


class NotificationSummaryResponse(BaseSchema):
    unread_count: int
    notifications: list[NotificationResponse]
