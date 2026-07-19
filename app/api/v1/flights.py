from datetime import datetime

from fastapi import APIRouter, Query, status

from app.dependencies.auth import CurrentUser
from app.models.flight_booking import FlightBooking
from app.repositories.flight_booking_repository import FlightBookingRepository
from app.repositories.trip_repository import TripRepository
from app.schemas.flight import FlightBookingResponse, FlightOffer, FlightSearchRequest, SaveFlightRequest
from app.services.flight_service import FlightService

router = APIRouter(prefix="/trips/{trip_id}/flights", tags=["Flights"])


def _get_service() -> FlightService:
    return FlightService(FlightBookingRepository(), TripRepository())


@router.get("/search", response_model=list[FlightOffer])
async def search_flights(
    trip_id: str,
    current_user: CurrentUser,
    origin: str = Query(..., min_length=3, max_length=3),
    destination: str = Query(..., min_length=3, max_length=3),
    departure_date: datetime = Query(...),
    return_date: datetime | None = None,
    adults: int = Query(default=1, ge=1, le=9),
):
    svc = _get_service()
    data = FlightSearchRequest(
        origin=origin.upper(),
        destination=destination.upper(),
        departure_date=departure_date,
        return_date=return_date,
        adults=adults,
    )
    return await svc.search(data)


@router.post("", status_code=status.HTTP_201_CREATED, response_model=FlightBookingResponse)
async def save_flight(trip_id: str, data: SaveFlightRequest, current_user: CurrentUser):
    svc = _get_service()
    booking = await svc.save_flight(trip_id, str(current_user.id), data)
    return _to_response(booking)


@router.get("", response_model=FlightBookingResponse)
async def get_flight(trip_id: str, current_user: CurrentUser):
    svc = _get_service()
    booking = await svc.get_flight(trip_id, str(current_user.id))
    return _to_response(booking)


@router.delete("", status_code=status.HTTP_204_NO_CONTENT)
async def delete_flight(trip_id: str, current_user: CurrentUser):
    svc = _get_service()
    await svc.delete_flight(trip_id, str(current_user.id))


def _to_response(booking: FlightBooking) -> FlightBookingResponse:
    return FlightBookingResponse(
        id=str(booking.id),
        trip_id=booking.trip_id,
        origin=booking.origin,
        destination=booking.destination,
        departure_date=booking.departure_date,
        return_date=booking.return_date,
        airline=booking.airline,
        price=booking.price,
        currency=booking.currency,
        deep_link=booking.deep_link,
        created_at=booking.created_at,
    )
