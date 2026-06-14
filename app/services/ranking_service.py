from app.repositories.stats_repository import StatsRepository
from app.repositories.user_repository import UserRepository
from app.schemas.ranking import RankingEntryResponse
from app.schemas.user import UserMiniResponse
from app.utils.pagination import compute_skip


class RankingService:
    def __init__(self, stats_repo: StatsRepository, user_repo: UserRepository):
        self._stats_repo = stats_repo
        self._user_repo = user_repo

    async def get_global(self, page: int, page_size: int) -> list[RankingEntryResponse]:
        skip = compute_skip(page, page_size)
        entries = await self._stats_repo.get_global_leaderboard(skip, page_size)
        return await self._to_response(entries, skip)

    async def get_by_country(self, country: str, page: int, page_size: int) -> list[RankingEntryResponse]:
        skip = compute_skip(page, page_size)
        entries = await self._stats_repo.get_country_leaderboard(country, skip, page_size)
        return await self._to_response(entries, skip)

    async def get_by_city(self, city: str, page: int, page_size: int) -> list[RankingEntryResponse]:
        skip = compute_skip(page, page_size)
        entries = await self._stats_repo.get_city_leaderboard(city, skip, page_size)
        return await self._to_response(entries, skip)

    async def get_user_rank(self, user_id: str) -> int:
        return await self._stats_repo.get_user_rank_global(user_id)

    async def _to_response(self, stats_list, base_rank_offset: int) -> list[RankingEntryResponse]:
        result = []
        for rank_offset, stats in enumerate(stats_list, start=1):
            try:
                user = await self._user_repo.get_by_id(stats.user_id)
            except Exception:
                continue
            result.append(
                RankingEntryResponse(
                    rank=base_rank_offset + rank_offset,
                    user=UserMiniResponse(
                        id=str(user.id),
                        username=user.username,
                        avatar_url=user.avatar_url,
                        points=user.points,
                    ),
                    points=stats.points,
                    places_visited=stats.places_visited,
                    badges=stats.badges,
                    collections_completed=stats.collections_completed,
                )
            )
        return result
