from fastapi import APIRouter, Depends, Query

from app.dependencies.pagination import PaginationParams
from app.repositories.stats_repository import StatsRepository
from app.repositories.user_repository import UserRepository
from app.schemas.ranking import RankingEntryResponse
from app.services.ranking_service import RankingService

router = APIRouter(prefix="/rankings", tags=["Rankings"])


def _get_ranking_service() -> RankingService:
    return RankingService(StatsRepository(), UserRepository())


@router.get("/global", response_model=list[RankingEntryResponse])
async def global_ranking(pagination: PaginationParams = Depends()):
    svc = _get_ranking_service()
    return await svc.get_global(pagination.page, pagination.page_size)


@router.get("/country", response_model=list[RankingEntryResponse])
async def country_ranking(
    country: str = Query(..., min_length=2),
    pagination: PaginationParams = Depends(),
):
    svc = _get_ranking_service()
    return await svc.get_by_country(country, pagination.page, pagination.page_size)


@router.get("/city", response_model=list[RankingEntryResponse])
async def city_ranking(
    city: str = Query(..., min_length=2),
    pagination: PaginationParams = Depends(),
):
    svc = _get_ranking_service()
    return await svc.get_by_city(city, pagination.page, pagination.page_size)
