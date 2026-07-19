from fastapi import APIRouter, status

from app.dependencies.auth import CurrentUser
from app.models.itinerary import Itinerary
from app.repositories.itinerary_repository import ItineraryRepository
from app.repositories.trip_repository import TripRepository
from app.schemas.itinerary import ItineraryResponse, UpdateItineraryRequest
from app.services.itinerary_service import ItineraryService

router = APIRouter(prefix="/trips/{trip_id}/itinerary", tags=["Itinerary"])


def _get_service() -> ItineraryService:
    return ItineraryService(ItineraryRepository(), TripRepository())


@router.post("", status_code=status.HTTP_201_CREATED, response_model=ItineraryResponse)
async def generate_itinerary(trip_id: str, current_user: CurrentUser):
    svc = _get_service()
    itinerary = await svc.generate_for_trip(trip_id, str(current_user.id))
    return _to_response(itinerary)


@router.get("", response_model=ItineraryResponse)
async def get_itinerary(trip_id: str, current_user: CurrentUser):
    svc = _get_service()
    itinerary = await svc.get_by_trip(trip_id, str(current_user.id))
    return _to_response(itinerary)


@router.put("", response_model=ItineraryResponse)
async def update_itinerary(trip_id: str, data: UpdateItineraryRequest, current_user: CurrentUser):
    svc = _get_service()
    itinerary = await svc.update_itinerary(trip_id, str(current_user.id), data)
    return _to_response(itinerary)


@router.delete("", status_code=status.HTTP_204_NO_CONTENT)
async def delete_itinerary(trip_id: str, current_user: CurrentUser):
    svc = _get_service()
    await svc.delete_itinerary(trip_id, str(current_user.id))


def _to_response(itinerary: Itinerary) -> ItineraryResponse:
    return ItineraryResponse(
        id=str(itinerary.id),
        trip_id=itinerary.trip_id,
        user_id=itinerary.user_id,
        days=[d.model_dump() for d in itinerary.days],
        created_at=itinerary.created_at,
        updated_at=itinerary.updated_at,
    )
