from fastapi import APIRouter, Depends, Query

from app.core.constants import FeedMode
from app.dependencies.auth import CurrentUser, OptionalUser
from app.dependencies.pagination import PaginationParams
from app.repositories.follow_repository import FollowRepository
from app.repositories.photo_repository import PhotoLikeRepository, PhotoRepository, PhotoSaveRepository
from app.repositories.place_repository import PlaceRepository
from app.repositories.user_repository import UserRepository
from app.schemas.photo import FeedItemResponse
from app.services.feed_service import FeedService

router = APIRouter(prefix="/feed", tags=["Feed"])


def _get_feed_service() -> FeedService:
    return FeedService(
        photo_repo=PhotoRepository(),
        like_repo=PhotoLikeRepository(),
        save_repo=PhotoSaveRepository(),
        user_repo=UserRepository(),
        place_repo=PlaceRepository(),
        follow_repo=FollowRepository(),
    )


@router.get("", response_model=list[FeedItemResponse])
async def get_feed(
    current_user: OptionalUser,
    mode: FeedMode = Query(default=FeedMode.RECENT),
    pagination: PaginationParams = Depends(),
):
    svc = _get_feed_service()
    user_id = str(current_user.id) if current_user else "anonymous"
    return await svc.get_feed(
        current_user_id=user_id,
        mode=mode,
        page=pagination.page,
        page_size=pagination.page_size,
    )
