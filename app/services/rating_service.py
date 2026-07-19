from datetime import UTC, datetime

from app.core.exceptions import ForbiddenError, NotFoundError
from app.models.rating import Rating
from app.repositories.place_repository import PlaceRepository
from app.repositories.rating_repository import RatingRepository
from app.repositories.visit_repository import VisitRepository


class RatingService:
    def __init__(
        self,
        rating_repo: RatingRepository,
        place_repo: PlaceRepository,
        visit_repo: VisitRepository,
    ):
        self._repo = rating_repo
        self._place_repo = place_repo
        self._visit_repo = visit_repo

    async def rate_place(self, user_id: str, place_id: str, score: int, review: str | None) -> Rating:
        await self._place_repo.get_by_id(place_id)  # raises NotFoundError if invalid

        has_visited = await self._visit_repo.has_verified_visit(user_id, place_id)
        if not has_visited:
            raise ForbiddenError("Debes visitar el lugar (check-in verificado) antes de calificarlo")

        existing = await self._repo.get_by_user_and_place(user_id, place_id)
        if existing:
            existing.score = score
            existing.review = review
            existing.updated_at = datetime.now(UTC)
            await existing.save()
            rating = existing
        else:
            rating = Rating(user_id=user_id, place_id=place_id, score=score, review=review)
            await rating.save()

        await self._recompute_place_rating(place_id)
        return rating

    async def get_place_ratings(self, place_id: str, page: int, page_size: int) -> list[Rating]:
        from app.utils.pagination import compute_skip
        skip = compute_skip(page, page_size)
        return await self._repo.get_place_ratings(place_id, skip=skip, limit=page_size)

    async def delete_rating(self, user_id: str, place_id: str) -> None:
        existing = await self._repo.get_by_user_and_place(user_id, place_id)
        if not existing:
            raise NotFoundError("Rating not found")
        await existing.delete()
        await self._recompute_place_rating(place_id)

    async def _recompute_place_rating(self, place_id: str) -> None:
        avg, count = await self._repo.compute_average(place_id)
        place = await self._place_repo.get_by_id(place_id)
        place.average_rating = avg
        place.rating_count = count
        await place.save()
