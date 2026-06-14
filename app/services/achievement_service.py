"""
AchievementService — Event-driven engine triggered after every validated visit.

Flow per visit validation:
  1. Load all badge requirements
  2. Get the set of place_ids the user has already visited
  3. For each badge requirement, check if the user's visited set satisfies all required places
  4. Skip badges the user already holds
  5. Award new badges, grant points, send notifications
  6. Check collection progress and award completed collections
"""
import logging
from datetime import UTC, datetime

from app.models.badge import UserBadge
from app.models.user_stats import UserStats
from app.repositories.badge_repository import BadgeRepository, BadgeRequirementRepository, UserBadgeRepository
from app.repositories.collection_repository import CollectionRepository, UserCollectionProgressRepository
from app.repositories.user_repository import UserRepository
from app.repositories.visit_repository import VisitRepository
from app.services.notification_service import NotificationService
from app.services.points_service import PointsService

logger = logging.getLogger(__name__)


class AchievementService:
    def __init__(
        self,
        visit_repo: VisitRepository,
        badge_repo: BadgeRepository,
        badge_req_repo: BadgeRequirementRepository,
        user_badge_repo: UserBadgeRepository,
        collection_repo: CollectionRepository,
        collection_progress_repo: UserCollectionProgressRepository,
        user_repo: UserRepository,
        points_svc: PointsService,
        notification_svc: NotificationService,
    ):
        self._visit_repo = visit_repo
        self._badge_repo = badge_repo
        self._badge_req_repo = badge_req_repo
        self._user_badge_repo = user_badge_repo
        self._collection_repo = collection_repo
        self._collection_progress_repo = collection_progress_repo
        self._user_repo = user_repo
        self._points_svc = points_svc
        self._notification_svc = notification_svc

    async def process_visit(self, user_id: str, place_id: str) -> dict:
        """Run full achievement check after a visit is validated. Returns summary."""
        visited_ids = set(await self._visit_repo.get_user_visited_place_ids(user_id))
        result = {
            "new_badges": [],
            "new_collections": [],
            "points_earned": 0,
        }

        # Award visit points
        pts = await self._points_svc.award_visit(user_id)
        result["points_earned"] += pts

        # Badge evaluation
        new_badges = await self._evaluate_badges(user_id, visited_ids)
        result["new_badges"] = new_badges
        for badge in new_badges:
            badge_pts = await self._points_svc.award_badge_earned(user_id, badge["points"])
            result["points_earned"] += badge_pts
            await self._notification_svc.notify_new_badge(user_id, badge["name"], badge["id"])

        # Collection evaluation
        new_collections = await self._evaluate_collections(user_id, visited_ids)
        result["new_collections"] = new_collections
        for col in new_collections:
            col_pts = await self._points_svc.award_collection_completed(user_id)
            result["points_earned"] += col_pts
            await self._notification_svc.notify_collection_completed(user_id, col["name"], col["id"])

        # Update denormalized counter on user
        await self._user_repo.increment_counter(user_id, "badges_count", len(new_badges))

        logger.info(
            "Achievement check for user=%s place=%s → badges=%d collections=%d points=%d",
            user_id,
            place_id,
            len(new_badges),
            len(new_collections),
            result["points_earned"],
        )
        return result

    async def _evaluate_badges(self, user_id: str, visited_ids: set[str]) -> list[dict]:
        all_requirements = await self._badge_req_repo.get_all()
        existing_badge_ids = await self._user_badge_repo.get_user_badge_ids(user_id)
        newly_earned = []

        for req in all_requirements:
            if req.badge_id in existing_badge_ids:
                continue
            required = set(req.place_ids)
            if not required:
                continue
            if required.issubset(visited_ids):
                badge = await self._badge_repo.get_by_id_or_none(req.badge_id)
                if not badge or not badge.is_active:
                    continue
                user_badge = UserBadge(user_id=user_id, badge_id=req.badge_id)
                await user_badge.save()
                newly_earned.append({"id": req.badge_id, "name": badge.name, "points": badge.points})

        return newly_earned

    async def _evaluate_collections(self, user_id: str, visited_ids: set[str]) -> list[dict]:
        all_collections = await self._collection_repo.get_all_active()
        newly_completed = []

        for collection in all_collections:
            required = set(collection.place_ids)
            if not required:
                continue
            visited_in_col = visited_ids.intersection(required)
            col_id = str(collection.id)
            is_complete = visited_in_col == required

            # Check if already completed
            existing = await self._collection_progress_repo.get_progress(user_id, col_id)
            was_complete = existing.completed if existing else False

            completed_at = datetime.now(UTC) if (is_complete and not was_complete) else (
                existing.completed_at if existing else None
            )

            await self._collection_progress_repo.upsert_progress(
                user_id=user_id,
                collection_id=col_id,
                visited_place_ids=list(visited_in_col),
                completed=is_complete,
                completed_at=completed_at,
            )

            if is_complete and not was_complete:
                newly_completed.append({"id": col_id, "name": collection.name})

        return newly_completed
