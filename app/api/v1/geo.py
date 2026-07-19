from fastapi import APIRouter, Query

from app.dependencies.auth import CurrentUser
from app.schemas.geo import CitySuggestion
from app.services.geo_service import GeoService

router = APIRouter(prefix="/geo", tags=["Geo"])


@router.get("/cities", response_model=list[CitySuggestion])
async def search_cities(current_user: CurrentUser, q: str = Query(..., min_length=2, max_length=80)):
    svc = GeoService()
    results = await svc.search_cities(q)
    return [CitySuggestion(**r) for r in results]
