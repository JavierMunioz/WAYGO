import re

import httpx

from app.core.config import settings
from app.core.exceptions import ExternalServiceError, ForbiddenError, NotFoundError
from app.models.flight_booking import FlightBooking
from app.models.trip import Trip
from app.repositories.flight_booking_repository import FlightBookingRepository
from app.repositories.trip_repository import TripRepository
from app.schemas.flight import FlightOffer, FlightSearchRequest, SaveFlightRequest

_ISO_DURATION_RE = re.compile(r"PT(?:(\d+)H)?(?:(\d+)M)?")


def _parse_duration_minutes(duration: str | None) -> int:
    if not duration:
        return 0
    match = _ISO_DURATION_RE.match(duration)
    if not match:
        return 0
    hours = int(match.group(1) or 0)
    minutes = int(match.group(2) or 0)
    return hours * 60 + minutes


class FlightService:
    def __init__(self, flight_repo: FlightBookingRepository, trip_repo: TripRepository):
        self._repo = flight_repo
        self._trip_repo = trip_repo

    async def search(self, data: FlightSearchRequest) -> list[FlightOffer]:
        slices = [
            {
                "origin": data.origin,
                "destination": data.destination,
                "departure_date": data.departure_date.strftime("%Y-%m-%d"),
            }
        ]
        if data.return_date:
            slices.append(
                {
                    "origin": data.destination,
                    "destination": data.origin,
                    "departure_date": data.return_date.strftime("%Y-%m-%d"),
                }
            )

        body = {
            "data": {
                "slices": slices,
                "passengers": [{"type": "adult"} for _ in range(data.adults)],
                "cabin_class": "economy",
            }
        }

        async with httpx.AsyncClient(timeout=20.0) as client:
            try:
                response = await client.post(
                    f"{settings.DUFFEL_API_BASE_URL}/air/offer_requests",
                    json=body,
                    headers={
                        "Authorization": f"Bearer {settings.DUFFEL_API_KEY}",
                        "Duffel-Version": settings.DUFFEL_VERSION,
                        "Content-Type": "application/json",
                        "Accept": "application/json",
                    },
                )
                response.raise_for_status()
            except httpx.HTTPError as e:
                raise ExternalServiceError(f"Flight search failed: {e}")

        raw_offers = response.json().get("data", {}).get("offers", [])
        raw_offers.sort(key=lambda o: float(o["total_amount"]))

        offers: list[FlightOffer] = []
        for offer in raw_offers[:20]:
            slices_data = offer.get("slices", [])
            if not slices_data:
                continue
            outbound = slices_data[0]
            outbound_segments = outbound.get("segments", [])
            if not outbound_segments:
                continue

            return_slice = slices_data[1] if len(slices_data) > 1 else None
            return_segments = return_slice.get("segments", []) if return_slice else []

            offers.append(
                FlightOffer(
                    booking_token=offer["id"],
                    airline=offer.get("owner", {}).get("name", "N/A"),
                    price=float(offer["total_amount"]),
                    currency=offer["total_currency"],
                    departure_time=outbound_segments[0]["departing_at"],
                    arrival_time=outbound_segments[-1]["arriving_at"],
                    return_departure_time=return_segments[0]["departing_at"] if return_segments else None,
                    return_arrival_time=return_segments[-1]["arriving_at"] if return_segments else None,
                    duration_minutes=_parse_duration_minutes(outbound.get("duration")),
                    deep_link="",
                )
            )
        return offers

    async def save_flight(self, trip_id: str, user_id: str, data: SaveFlightRequest) -> FlightBooking:
        trip = await self._trip_repo.get_by_id(trip_id)
        self._ensure_owner(trip, user_id)

        existing = await self._repo.get_by_trip_id(trip_id)
        if existing:
            for key, val in data.model_dump().items():
                setattr(existing, key, val)
            await existing.save()
            return existing

        booking = FlightBooking(trip_id=trip_id, user_id=user_id, **data.model_dump())
        await booking.save()
        return booking

    async def get_flight(self, trip_id: str, user_id: str) -> FlightBooking:
        trip = await self._trip_repo.get_by_id(trip_id)
        self._ensure_owner(trip, user_id)

        booking = await self._repo.get_by_trip_id(trip_id)
        if not booking:
            raise NotFoundError("No flight booked for this trip")
        return booking

    async def delete_flight(self, trip_id: str, user_id: str) -> None:
        booking = await self.get_flight(trip_id, user_id)
        await booking.delete()

    @staticmethod
    def _ensure_owner(trip: Trip, user_id: str) -> None:
        if trip.user_id != user_id:
            raise ForbiddenError("You do not own this trip")
