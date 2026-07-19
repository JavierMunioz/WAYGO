from fastapi import APIRouter, Depends, status

from app.dependencies.auth import CurrentUser
from app.dependencies.pagination import PaginationParams
from app.models.trip import Trip
from app.repositories.trip_repository import TripRepository
from app.schemas.trip import CreateTripRequest, TripResponse, UpdateTripRequest
from app.services.trip_service import TripService

router = APIRouter(prefix="/trips", tags=["Trips"])


def _get_trip_service() -> TripService:
    return TripService(TripRepository())


@router.post("", status_code=status.HTTP_201_CREATED, response_model=TripResponse)
async def create_trip(data: CreateTripRequest, current_user: CurrentUser):
    svc = _get_trip_service()
    trip = await svc.create_trip(str(current_user.id), data)
    return _to_response(trip)


@router.get("/me", response_model=list[TripResponse])
async def get_my_trips(current_user: CurrentUser, pagination: PaginationParams = Depends()):
    svc = _get_trip_service()
    trips = await svc.list_user_trips(str(current_user.id), pagination.page, pagination.page_size)
    return [_to_response(t) for t in trips]


@router.get("/{trip_id}", response_model=TripResponse)
async def get_trip(trip_id: str, current_user: CurrentUser):
    svc = _get_trip_service()
    trip = await svc.get_trip(trip_id, str(current_user.id))
    return _to_response(trip)


@router.patch("/{trip_id}", response_model=TripResponse)
async def update_trip(trip_id: str, data: UpdateTripRequest, current_user: CurrentUser):
    svc = _get_trip_service()
    trip = await svc.update_trip(trip_id, str(current_user.id), data)
    return _to_response(trip)


@router.delete("/{trip_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_trip(trip_id: str, current_user: CurrentUser):
    svc = _get_trip_service()
    await svc.delete_trip(trip_id, str(current_user.id))


def _to_response(trip: Trip) -> TripResponse:
    return TripResponse(
        id=str(trip.id),
        user_id=trip.user_id,
        title=trip.title,
        destination_country=trip.destination_country,
        destination_city=trip.destination_city,
        start_date=trip.start_date,
        end_date=trip.end_date,
        days=trip.days,
        availability=trip.availability,
        interests=trip.interests,
        status=trip.status,
        cover_image=trip.cover_image,
        created_at=trip.created_at,
        updated_at=trip.updated_at,
    )
