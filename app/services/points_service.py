from app.core.config import settings
from app.repositories.stats_repository import StatsRepository
from app.repositories.user_repository import UserRepository


class PointsService:
    def __init__(self, user_repo: UserRepository, stats_repo: StatsRepository):
        self._user_repo = user_repo
        self._stats_repo = stats_repo

    async def award_visit(self, user_id: str) -> int:
        pts = settings.POINTS_VISIT_PLACE
        await self._user_repo.increment_points(user_id, pts)
        await self._stats_repo.increment(user_id, points=pts, places_visited=1)
        return pts

    async def award_photo_upload(self, user_id: str) -> int:
        pts = settings.POINTS_UPLOAD_PHOTO
        await self._user_repo.increment_points(user_id, pts)
        await self._stats_repo.increment(user_id, points=pts, photos_uploaded=1)
        return pts

    async def award_like_received(self, user_id: str) -> int:
        pts = settings.POINTS_RECEIVE_LIKE
        await self._user_repo.increment_points(user_id, pts)
        await self._stats_repo.increment(user_id, points=pts, likes_received=1)
        return pts

    async def award_collection_completed(self, user_id: str) -> int:
        pts = settings.POINTS_COMPLETE_COLLECTION
        await self._user_repo.increment_points(user_id, pts)
        await self._stats_repo.increment(user_id, points=pts, collections_completed=1)
        return pts

    async def award_badge_earned(self, user_id: str, badge_points: int) -> int:
        await self._user_repo.increment_points(user_id, badge_points)
        await self._stats_repo.increment(user_id, points=badge_points, badges=1)
        return badge_points
