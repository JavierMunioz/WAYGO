from app.repositories.badge_repository import BadgeRepository, BadgeRequirementRepository, UserBadgeRepository
from app.repositories.visit_repository import VisitRepository
from app.schemas.badge import BadgeWithProgressResponse


class BadgeService:
    def __init__(
        self,
        badge_repo: BadgeRepository,
        badge_req_repo: BadgeRequirementRepository,
        user_badge_repo: UserBadgeRepository,
        visit_repo: VisitRepository,
    ):
        self._badge_repo = badge_repo
        self._badge_req_repo = badge_req_repo
        self._user_badge_repo = user_badge_repo
        self._visit_repo = visit_repo

    async def get_all_badges_with_progress(self, user_id: str) -> list[BadgeWithProgressResponse]:
        all_badges = await self._badge_repo.get_all_active()
        visited_ids = set(await self._visit_repo.get_user_visited_place_ids(user_id))
        earned_ids = await self._user_badge_repo.get_user_badge_ids(user_id)
        all_requirements = {req.badge_id: req for req in await self._badge_req_repo.get_all()}

        result = []
        for badge in all_badges:
            badge_id = str(badge.id)
            req = all_requirements.get(badge_id)
            required_count = len(req.place_ids) if req else 0
            visited_count = len(visited_ids.intersection(set(req.place_ids))) if req else 0
            progress_pct = (visited_count / required_count * 100) if required_count > 0 else 0

            result.append(
                BadgeWithProgressResponse(
                    id=badge_id,
                    name=badge.name,
                    slug=badge.slug,
                    description=badge.description,
                    image_url=badge.image_url,
                    points=badge.points,
                    city=badge.city,
                    country=badge.country,
                    level=badge.level,
                    required_places=required_count,
                    visited_places=visited_count,
                    progress_pct=round(progress_pct, 1),
                    completed=badge_id in earned_ids,
                )
            )
        return result
