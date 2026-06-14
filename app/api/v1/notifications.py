from fastapi import APIRouter, Depends, Query, status

from app.dependencies.auth import CurrentUser
from app.dependencies.pagination import PaginationParams
from app.repositories.notification_repository import NotificationRepository
from app.schemas.common import MessageResponse
from app.schemas.notification import NotificationResponse
from app.services.notification_service import NotificationService

router = APIRouter(prefix="/notifications", tags=["Notifications"])


def _get_notification_service() -> NotificationService:
    return NotificationService(NotificationRepository())


@router.get("", response_model=list[NotificationResponse])
async def get_notifications(
    current_user: CurrentUser,
    unread_only: bool = Query(default=False),
    pagination: PaginationParams = Depends(),
):
    svc = _get_notification_service()
    notifs, _ = await svc.get_user_notifications(
        str(current_user.id), unread_only, pagination.page, pagination.page_size
    )
    return [
        NotificationResponse(
            id=str(n.id),
            type=n.type,
            title=n.title,
            body=n.body,
            data=n.data,
            read=n.read,
            created_at=n.created_at,
        )
        for n in notifs
    ]


@router.get("/unread-count")
async def get_unread_count(current_user: CurrentUser):
    repo = NotificationRepository()
    count = await repo.count_unread(str(current_user.id))
    return {"unread_count": count}


@router.post("/{notification_id}/read", status_code=status.HTTP_204_NO_CONTENT)
async def mark_as_read(notification_id: str, current_user: CurrentUser):
    svc = _get_notification_service()
    await svc.mark_read(notification_id)


@router.post("/read-all", status_code=status.HTTP_204_NO_CONTENT)
async def mark_all_as_read(current_user: CurrentUser):
    svc = _get_notification_service()
    await svc.mark_all_read(str(current_user.id))
