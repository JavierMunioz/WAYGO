from fastapi import APIRouter, Depends, File, Form, UploadFile, status

from app.dependencies.auth import CurrentUser
from app.dependencies.pagination import PaginationParams
from app.repositories.notification_repository import NotificationRepository
from app.repositories.photo_repository import PhotoLikeRepository, PhotoRepository, PhotoSaveRepository
from app.repositories.place_repository import PlaceRepository
from app.repositories.stats_repository import StatsRepository
from app.repositories.user_repository import UserRepository
from app.repositories.visit_repository import VisitRepository
from app.schemas.common import MessageResponse
from app.schemas.photo import PhotoResponse
from app.services.like_service import LikeService
from app.services.notification_service import NotificationService
from app.services.photo_service import PhotoService
from app.services.points_service import PointsService

router = APIRouter(prefix="/photos", tags=["Photos"])


def _get_photo_service() -> PhotoService:
    return PhotoService(
        photo_repo=PhotoRepository(),
        visit_repo=VisitRepository(),
        place_repo=PlaceRepository(),
        user_repo=UserRepository(),
    )


def _get_like_service() -> LikeService:
    return LikeService(
        like_repo=PhotoLikeRepository(),
        photo_repo=PhotoRepository(),
        user_repo=UserRepository(),
        points_svc=PointsService(UserRepository(), StatsRepository()),
        notification_svc=NotificationService(NotificationRepository()),
        place_repo=PlaceRepository(),
    )


@router.post("", status_code=status.HTTP_201_CREATED, response_model=PhotoResponse)
async def upload_photo(
    current_user: CurrentUser,
    visit_id: str = Form(...),
    place_id: str = Form(...),
    caption: str | None = Form(None),
    file: UploadFile = File(...),
):
    svc = _get_photo_service()
    content = await file.read()
    photo = await svc.upload_photo(
        user_id=str(current_user.id),
        visit_id=visit_id,
        place_id=place_id,
        file_content=content,
        content_type=file.content_type or "image/jpeg",
        caption=caption,
    )
    return _to_response(photo)


@router.get("/{photo_id}", response_model=PhotoResponse)
async def get_photo(photo_id: str):
    svc = _get_photo_service()
    photo = await svc.get_photo(photo_id)
    return _to_response(photo)


@router.delete("/{photo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_photo(photo_id: str, current_user: CurrentUser):
    svc = _get_photo_service()
    await svc.delete_photo(str(current_user.id), photo_id)


@router.post("/{photo_id}/like", status_code=status.HTTP_204_NO_CONTENT)
async def like_photo(photo_id: str, current_user: CurrentUser):
    svc = _get_like_service()
    await svc.like_photo(str(current_user.id), photo_id, current_user.username)


@router.delete("/{photo_id}/like", status_code=status.HTTP_204_NO_CONTENT)
async def unlike_photo(photo_id: str, current_user: CurrentUser):
    svc = _get_like_service()
    await svc.unlike_photo(str(current_user.id), photo_id)


@router.get("/{photo_id}/likes")
async def get_photo_likes(photo_id: str, pagination: PaginationParams = Depends()):
    svc = _get_like_service()
    likes = await svc.get_photo_likers(photo_id, pagination.page, pagination.page_size)
    user_repo = UserRepository()
    result = []
    for like in likes:
        try:
            u = await user_repo.get_by_id(like.user_id)
            result.append({"user_id": like.user_id, "username": u.username, "liked_at": like.created_at})
        except Exception:
            pass
    return result


@router.post("/{photo_id}/save", status_code=status.HTTP_204_NO_CONTENT)
async def save_photo(photo_id: str, current_user: CurrentUser):
    await PhotoSaveRepository().save(str(current_user.id), photo_id)


@router.delete("/{photo_id}/save", status_code=status.HTTP_204_NO_CONTENT)
async def unsave_photo(photo_id: str, current_user: CurrentUser):
    await PhotoSaveRepository().unsave(str(current_user.id), photo_id)


def _to_response(photo) -> PhotoResponse:
    return PhotoResponse(
        id=str(photo.id),
        user_id=photo.user_id,
        place_id=photo.place_id,
        visit_id=photo.visit_id,
        image_url=photo.image_url,
        caption=photo.caption,
        likes_count=photo.likes_count,
        comments_count=photo.comments_count,
        created_at=photo.created_at,
    )
