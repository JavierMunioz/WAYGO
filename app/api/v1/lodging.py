from datetime import datetime

from fastapi import APIRouter, Query, status

from app.dependencies.auth import CurrentUser
from app.models.lodging_booking import LodgingBooking
from app.repositories.flight_booking_repository import FlightBookingRepository
from app.repositories.hotelbeds_destination_repository import HotelbedsDestinationRepository
from app.repositories.lodging_booking_repository import LodgingBookingRepository
from app.repositories.trip_repository import TripRepository
from app.schemas.lodging import (
    ConfirmLodgingBookingRequest,
    DestinationSuggestion,
    HotelOffer,
    LodgingBookingResponse,
    LodgingSearchRequest,
    SaveLodgingRequest,
)
from app.services.hotelbeds_destination_service import HotelbedsDestinationService
from app.services.lodging_service import LodgingService

router = APIRouter(prefix="/trips/{trip_id}/lodging", tags=["Lodging"])
destinations_router = APIRouter(prefix="/lodging/destinations", tags=["Lodging"])


def _get_service() -> LodgingService:
    return LodgingService(LodgingBookingRepository(), TripRepository(), FlightBookingRepository())


@destinations_router.get("", response_model=list[DestinationSuggestion])
async def search_destinations(current_user: CurrentUser, q: str = Query(..., min_length=2, max_length=60)):
    svc = HotelbedsDestinationService(HotelbedsDestinationRepository())
    results = await svc.search(q)
    return [DestinationSuggestion(code=d.code, name=d.name, country_code=d.country_code) for d in results]


@router.get("/search", response_model=list[HotelOffer])
async def search_lodging(
    trip_id: str,
    current_user: CurrentUser,
    destination_code: str = Query(..., min_length=2, max_length=10),
    check_in: datetime = Query(...),
    check_out: datetime = Query(...),
    adults: int = Query(default=2, ge=1, le=10),
    rooms: int = Query(default=1, ge=1, le=5),
):
    svc = _get_service()
    data = LodgingSearchRequest(
        destination_code=destination_code,
        check_in=check_in,
        check_out=check_out,
        adults=adults,
        rooms=rooms,
    )
    return await svc.search(data)


@router.post("", status_code=status.HTTP_201_CREATED, response_model=LodgingBookingResponse)
async def save_lodging(trip_id: str, data: SaveLodgingRequest, current_user: CurrentUser):
    svc = _get_service()
    booking = await svc.save_lodging(trip_id, str(current_user.id), data)
    return _to_response(booking)


@router.get("", response_model=LodgingBookingResponse)
async def get_lodging(trip_id: str, current_user: CurrentUser):
    svc = _get_service()
    booking = await svc.get_lodging(trip_id, str(current_user.id))
    return _to_response(booking)


@router.delete("", status_code=status.HTTP_204_NO_CONTENT)
async def delete_lodging(trip_id: str, current_user: CurrentUser):
    svc = _get_service()
    await svc.delete_lodging(trip_id, str(current_user.id))


@router.post("/confirm", response_model=LodgingBookingResponse)
async def confirm_lodging(trip_id: str, data: ConfirmLodgingBookingRequest, current_user: CurrentUser):
    svc = _get_service()
    booking = await svc.confirm_booking(trip_id, str(current_user.id), data.holder_name, data.holder_surname)
    return _to_response(booking)


def _to_response(booking: LodgingBooking) -> LodgingBookingResponse:
    return LodgingBookingResponse(
        id=str(booking.id),
        trip_id=booking.trip_id,
        hotel_code=booking.hotel_code,
        hotel_name=booking.hotel_name,
        room_name=booking.room_name,
        board_name=booking.board_name,
        check_in=booking.check_in,
        check_out=booking.check_out,
        price=booking.price,
        currency=booking.currency,
        status=booking.status,
        hotelbeds_reference=booking.hotelbeds_reference,
        created_at=booking.created_at,
    )
