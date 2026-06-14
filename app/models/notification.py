from datetime import UTC, datetime

from beanie import Document, Indexed
from pydantic import Field
from typing import Annotated

from app.core.constants import NotificationType


class Notification(Document):
    user_id: Annotated[str, Indexed()]
    type: NotificationType
    title: str
    body: str
    data: dict = Field(default_factory=dict)  # arbitrary payload (badge_id, photo_id, etc.)
    read: bool = False

    created_at: Annotated[datetime, Indexed()] = Field(default_factory=lambda: datetime.now(UTC))

    class Settings:
        name = "notifications"
