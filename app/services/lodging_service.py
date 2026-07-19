import hashlib
import time
from datetime import datetime

import httpx

from app.core.config import settings
from app.core.exceptions import ExternalServiceError, ForbiddenError, NotFoundError, ValidationError
from app.models.lodging_booking import LodgingBooking
from app.models.trip import Trip
from app.repositories.flight_booking_repository import FlightBookingRepository
from app.repositories.lodging_booking_repository import LodgingBookingRepository
from app.repositories.trip_repository import TripRepository
from app.schemas.lodging import HotelOffer, LodgingSearchRequest, SaveLodgingRequest


def _build_signature() -> str:
    raw = f"{settings.HOTELBEDS_API_KEY}{settings.HOTELBEDS_SECRET}{int(time.time())}"
    return hashlib.sha256(raw.encode()).hexdigest()


class LodgingService:
    def __init__(
        self,
        lodging_repo: LodgingBookingRepository,
        trip_repo: TripRepository,
        flight_repo: FlightBookingRepository,
    ):
        self._repo = lodging_repo
        self._trip_repo = trip_repo
        self._flight_repo = flight_repo

    async def search(self, data: LodgingSearchRequest) -> list[HotelOffer]:
        body = {
            "stay": {
                "checkIn": data.check_in.strftime("%Y-%m-%d"),
                "checkOut": data.check_out.strftime("%Y-%m-%d"),
            },
            "occupancies": [{"rooms": data.rooms, "adults": data.adults, "children": 0}],
            "destination": {"code": data.destination_code},
        }

        async with httpx.AsyncClient(timeout=20.0) as client:
            try:
                response = await client.post(
                    f"{settings.HOTELBEDS_API_BASE_URL}/hotel-api/1.0/hotels",
                    json=body,
                    headers={
                        "Api-key": settings.HOTELBEDS_API_KEY,
                        "X-Signature": _build_signature(),
                        "Accept": "application/json",
                        "Content-Type": "application/json",
                    },
                )
                response.raise_for_status()
            except httpx.HTTPError as e:
                raise ExternalServiceError(f"Lodging search failed: {e}")

        raw_hotels = response.json().get("hotels", {}).get("hotels", [])
        raw_hotels.sort(key=lambda h: float(h.get("minRate", 0)))

        offers: list[HotelOffer] = []
        for hotel in raw_hotels[:20]:
            rooms = hotel.get("rooms", [])
            if not rooms or not rooms[0].get("rates"):
                continue
            room = rooms[0]
            rate = room["rates"][0]

            offers.append(
                HotelOffer(
                    hotel_code=hotel["code"],
                    hotel_name=hotel["name"],
                    category_name=hotel.get("categoryName", ""),
                    destination_name=hotel.get("destinationName", ""),
                    latitude=float(hotel["latitude"]) if hotel.get("latitude") else None,
                    longitude=float(hotel["longitude"]) if hotel.get("longitude") else None,
                    price=float(rate["net"]),
                    currency=hotel.get("currency", "EUR"),
                    room_name=room.get("name", ""),
                    board_name=rate.get("boardName", ""),
                    rate_key=rate["rateKey"],
                )
            )
        return offers

    async def save_lodging(self, trip_id: str, user_id: str, data: SaveLodgingRequest) -> LodgingBooking:
        trip = await self._trip_repo.get_by_id(trip_id)
        self._ensure_owner(trip, user_id)
        await self._ensure_within_flight_return(trip_id, data.check_out)

        existing = await self._repo.get_by_trip_id(trip_id)
        if existing:
            for key, val in data.model_dump().items():
                setattr(existing, key, val)
            await existing.save()
            return existing

        booking = LodgingBooking(trip_id=trip_id, user_id=user_id, **data.model_dump())
        await booking.save()
        return booking

    async def get_lodging(self, trip_id: str, user_id: str) -> LodgingBooking:
        trip = await self._trip_repo.get_by_id(trip_id)
        self._ensure_owner(trip, user_id)

        booking = await self._repo.get_by_trip_id(trip_id)
        if not booking:
            raise NotFoundError("No lodging booked for this trip")
        return booking

    async def delete_lodging(self, trip_id: str, user_id: str) -> None:
        booking = await self.get_lodging(trip_id, user_id)
        await booking.delete()

    async def _ensure_within_flight_return(self, trip_id: str, check_out: datetime) -> None:
        """Regla de negocio: la estadía no puede exceder la fecha del tiquete de regreso."""
        flight = await self._flight_repo.get_by_trip_id(trip_id)
        if not flight or not flight.return_date:
            return

        # Mongo/Beanie devuelve datetimes naive (UTC); el request puede venir con tz-aware.
        check_out_naive = check_out.replace(tzinfo=None) if check_out.tzinfo else check_out
        return_date_naive = flight.return_date.replace(tzinfo=None) if flight.return_date.tzinfo else flight.return_date

        if check_out_naive > return_date_naive:
            raise ValidationError(
                "La fecha de salida del hospedaje no puede ser posterior a la fecha de regreso del vuelo"
            )

    @staticmethod
    def _ensure_owner(trip: Trip, user_id: str) -> None:
        if trip.user_id != user_id:
            raise ForbiddenError("You do not own this trip")
