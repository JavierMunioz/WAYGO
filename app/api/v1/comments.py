from fastapi import APIRouter, Depends, status

from app.dependencies.auth import CurrentUser
from app.dependencies.pagination import PaginationParams
from app.repositories.comment_repository import CommentRepository
from app.repositories.notification_repository import NotificationRepository
from app.repositories.photo_repository import PhotoRepository
from app.schemas.comment import CommentResponse, CreateCommentRequest, UpdateCommentRequest
from app.schemas.user import UserMiniResponse
from app.services.comment_service import CommentService
from app.services.notification_service import NotificationService

router = APIRouter(prefix="/photos/{photo_id}/comments", tags=["Comments"])


def _get_comment_service() -> CommentService:
    return CommentService(
        comment_repo=CommentRepository(),
        photo_repo=PhotoRepository(),
        notification_svc=NotificationService(NotificationRepository()),
    )


@router.get("", response_model=list[CommentResponse])
async def get_comments(photo_id: str, pagination: PaginationParams = Depends()):
    from app.repositories.user_repository import UserRepository
    svc = _get_comment_service()
    comments = await svc.get_photo_comments(photo_id, pagination.page, pagination.page_size)
    user_repo = UserRepository()
    result = []
    for c in comments:
        try:
            u = await user_repo.get_by_id(c.user_id)
            result.append(
                CommentResponse(
                    id=str(c.id),
                    photo_id=c.photo_id,
                    content=c.content,
                    created_at=c.created_at,
                    updated_at=c.updated_at,
                    user=UserMiniResponse(id=str(u.id), username=u.username, avatar_url=u.avatar_url, points=u.points),
                )
            )
        except Exception:
            pass
    return result


@router.post("", status_code=status.HTTP_201_CREATED, response_model=CommentResponse)
async def add_comment(photo_id: str, data: CreateCommentRequest, current_user: CurrentUser):
    from app.repositories.user_repository import UserRepository
    svc = _get_comment_service()
    comment = await svc.add_comment(str(current_user.id), photo_id, data.content, current_user.username)
    return CommentResponse(
        id=str(comment.id),
        photo_id=comment.photo_id,
        content=comment.content,
        created_at=comment.created_at,
        updated_at=comment.updated_at,
        user=UserMiniResponse(
            id=str(current_user.id),
            username=current_user.username,
            avatar_url=current_user.avatar_url,
            points=current_user.points,
        ),
    )


@router.patch("/{comment_id}", response_model=CommentResponse)
async def update_comment(photo_id: str, comment_id: str, data: UpdateCommentRequest, current_user: CurrentUser):
    svc = _get_comment_service()
    comment = await svc.update_comment(str(current_user.id), comment_id, data.content)
    return CommentResponse(
        id=str(comment.id),
        photo_id=comment.photo_id,
        content=comment.content,
        created_at=comment.created_at,
        updated_at=comment.updated_at,
        user=UserMiniResponse(
            id=str(current_user.id),
            username=current_user.username,
            avatar_url=current_user.avatar_url,
            points=current_user.points,
        ),
    )


@router.delete("/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_comment(photo_id: str, comment_id: str, current_user: CurrentUser):
    svc = _get_comment_service()
    await svc.delete_comment(str(current_user.id), comment_id, current_user.is_superuser)
