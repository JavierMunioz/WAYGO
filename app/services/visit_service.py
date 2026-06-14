from app.core.exceptions import GeoValidationError, NotFoundError
from app.models.visit import Visit
from app.repositories.place_repository import PlaceRepository
from app.repositories.user_repository import UserRepository
from app.repositories.visit_repository import VisitRepository
from app.schemas.visit import ValidateVisitRequest, VisitResponse
from app.utils.geo import haversine_distance


class VisitService:
    def __init__(
        self,
        visit_repo: VisitRepository,
        place_repo: PlaceRepository,
        user_repo: UserRepository,
    ):
        self._visit_repo = visit_repo
        self._place_repo = place_repo
        self._user_repo = user_repo

    async def validate_visit(self, user_id: str, data: ValidateVisitRequest) -> tuple[Visit, bool]:
        """
        Validates a user's GPS location against the place's validation radius.
        Returns (visit, is_new) — is_new=False means duplicate (already verified before).
        """
        place = await self._place_repo.get_by_id(data.place_id)

        # Check if already validated
        existing = await self._visit_repo.get_by_user_and_place(user_id, data.place_id)
        if existing:
            return existing, False  # idempotent — return existing visit

        place_lng, place_lat = place.location["coordinates"]
        distance = haversine_distance(data.latitude, data.longitude, place_lat, place_lng)

        verified = distance <= place.validation_radius

        visit = Visit(
            user_id=user_id,
            place_id=data.place_id,
            latitude=data.latitude,
            longitude=data.longitude,
            distance=round(distance, 2),
            verified=verified,
        )
        await visit.save()

        if not verified:
            raise GeoValidationError(
                f"You are {distance:.0f}m from the place (max {place.validation_radius:.0f}m required)"
            )

        # Increment place counter
        await self._place_repo.increment_counter(data.place_id, "total_visits")
        # Increment user places_visited_count
        await self._user_repo.increment_counter(user_id, "places_visited_count")

        return visit, True

    async def get_user_visits(self, user_id: str, page: int, page_size: int) -> list[Visit]:
        from app.utils.pagination import compute_skip
        skip = compute_skip(page, page_size)
        return await self._visit_repo.get_user_visits(user_id, skip=skip, limit=page_size)

    async def has_verified_visit(self, user_id: str, place_id: str) -> bool:
        return await self._visit_repo.has_verified_visit(user_id, place_id)
