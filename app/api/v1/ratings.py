from fastapi import APIRouter, Depends, status

from app.core.exceptions import NotFoundError
from app.dependencies.auth import CurrentUser
from app.dependencies.pagination import PaginationParams
from app.models.rating import Rating
from app.models.user import User
from app.repositories.place_repository import PlaceRepository
from app.repositories.rating_repository import RatingRepository
from app.repositories.user_repository import UserRepository
from app.repositories.visit_repository import VisitRepository
from app.schemas.rating import CreateRatingRequest, RatingResponse
from app.schemas.user import UserMiniResponse
from app.services.rating_service import RatingService

router = APIRouter(prefix="/places/{place_id}/ratings", tags=["Ratings"])


def _get_service() -> RatingService:
    return RatingService(RatingRepository(), PlaceRepository(), VisitRepository())


@router.get("", response_model=list[RatingResponse])
async def get_ratings(place_id: str, pagination: PaginationParams = Depends()):
    svc = _get_service()
    ratings = await svc.get_place_ratings(place_id, pagination.page, pagination.page_size)
    user_repo = UserRepository()
    result = []
    for r in ratings:
        try:
            u = await user_repo.get_by_id(r.user_id)
        except NotFoundError:
            continue  # orphaned rating — the user was deleted
        result.append(_to_response(r, u))
    return result


@router.post("", status_code=status.HTTP_201_CREATED, response_model=RatingResponse)
async def rate_place(place_id: str, data: CreateRatingRequest, current_user: CurrentUser):
    svc = _get_service()
    rating = await svc.rate_place(str(current_user.id), place_id, data.score, data.review)
    return _to_response(rating, current_user)


@router.delete("", status_code=status.HTTP_204_NO_CONTENT)
async def delete_rating(place_id: str, current_user: CurrentUser):
    svc = _get_service()
    await svc.delete_rating(str(current_user.id), place_id)


def _to_response(rating: Rating, user: User) -> RatingResponse:
    return RatingResponse(
        id=str(rating.id),
        place_id=rating.place_id,
        score=rating.score,
        review=rating.review,
        created_at=rating.created_at,
        updated_at=rating.updated_at,
        user=UserMiniResponse(
            id=str(user.id),
            username=user.username,
            avatar_url=user.avatar_url,
            points=user.points,
        ),
    )
