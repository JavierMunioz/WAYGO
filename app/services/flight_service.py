import re
from datetime import datetime

import httpx

from app.core.config import settings
from app.core.exceptions import ExternalServiceError, NotFoundError
from app.models.flight_booking import FlightBooking
from app.repositories.flight_booking_repository import FlightBookingRepository
from app.repositories.trip_repository import TripRepository
from app.schemas.flight import ConfirmFlightBookingRequest, FlightOffer, FlightSearchRequest, SaveFlightRequest
from app.utils.ownership import ensure_trip_owner

_ISO_DURATION_RE = re.compile(r"PT(?:(\d+)H)?(?:(\d+)M)?")

_DUFFEL_HEADERS = {
    "Authorization": f"Bearer {settings.DUFFEL_API_KEY}",
    "Duffel-Version": settings.DUFFEL_VERSION,
    "Accept": "application/json",
}


def _parse_duration_minutes(duration: str | None) -> int:
    if not duration:
        return 0
    match = _ISO_DURATION_RE.match(duration)
    if not match:
        return 0
    hours = int(match.group(1) or 0)
    minutes = int(match.group(2) or 0)
    return hours * 60 + minutes


def _offer_to_dict(offer: dict) -> dict:
    slices_data = offer.get("slices", [])
    outbound = slices_data[0] if slices_data else {}
    outbound_segments = outbound.get("segments", [])
    return_slice = slices_data[1] if len(slices_data) > 1 else None
    return_segments = return_slice.get("segments", []) if return_slice else []

    return {
        "airline": offer.get("owner", {}).get("name", "N/A"),
        "price": float(offer["total_amount"]),
        "currency": offer["total_currency"],
        "departure_time": outbound_segments[0]["departing_at"] if outbound_segments else None,
        "arrival_time": outbound_segments[-1]["arriving_at"] if outbound_segments else None,
        "return_departure_time": return_segments[0]["departing_at"] if return_segments else None,
        "return_arrival_time": return_segments[-1]["arriving_at"] if return_segments else None,
        "duration_minutes": _parse_duration_minutes(outbound.get("duration")),
    }


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
                    headers={**_DUFFEL_HEADERS, "Content-Type": "application/json"},
                )
                response.raise_for_status()
            except httpx.HTTPError as e:
                raise ExternalServiceError(f"Flight search failed: {e}")

        raw_offers = response.json().get("data", {}).get("offers", [])
        raw_offers.sort(key=lambda o: float(o["total_amount"]))

        offers: list[FlightOffer] = []
        for offer in raw_offers[:20]:
            if not offer.get("slices") or not offer["slices"][0].get("segments"):
                continue
            offers.append(FlightOffer(booking_token=offer["id"], deep_link="", **_offer_to_dict(offer)))
        return offers

    async def _fetch_raw_offer(self, booking_token: str) -> dict:
        async with httpx.AsyncClient(timeout=20.0) as client:
            try:
                response = await client.get(
                    f"{settings.DUFFEL_API_BASE_URL}/air/offers/{booking_token}",
                    headers=_DUFFEL_HEADERS,
                )
                response.raise_for_status()
            except httpx.HTTPError as e:
                raise ExternalServiceError(
                    f"No se pudo verificar la oferta de vuelo (puede haber expirado, busca de nuevo): {e}"
                )
        return response.json()["data"]

    async def _fetch_verified_offer(self, booking_token: str) -> dict:
        """Vuelve a pedirle la oferta a Duffel — nunca confiamos en el precio/fechas que mande el cliente."""
        return _offer_to_dict(await self._fetch_raw_offer(booking_token))

    async def save_flight(self, trip_id: str, user_id: str, data: SaveFlightRequest) -> FlightBooking:
        trip = await self._trip_repo.get_by_id(trip_id)
        ensure_trip_owner(trip, user_id)

        verified = await self._fetch_verified_offer(data.booking_token)
        fields = {
            "origin": data.origin,
            "destination": data.destination,
            "departure_date": datetime.fromisoformat(verified["departure_time"]) if verified["departure_time"] else data.departure_date,
            "return_date": datetime.fromisoformat(verified["return_departure_time"]) if verified["return_departure_time"] else data.return_date,
            "airline": verified["airline"],
            "price": verified["price"],
            "currency": verified["currency"],
            "booking_token": data.booking_token,
            "deep_link": data.deep_link,
        }

        existing = await self._repo.get_by_trip_id(trip_id)
        if existing:
            for key, val in fields.items():
                setattr(existing, key, val)
            await existing.save()
            return existing

        booking = FlightBooking(trip_id=trip_id, user_id=user_id, **fields)
        await booking.save()
        return booking

    async def confirm_booking(self, trip_id: str, user_id: str, data: ConfirmFlightBookingRequest) -> FlightBooking:
        """Crea la Order real en Duffel (`/air/orders`). En modo test usa el
        saldo simulado de la cuenta (gratis, sin plata real); en producción
        (`live_mode`) esto requiere saldo real prefondeado en la cuenta Duffel
        o aprobación de pago con tarjeta — no alcanza con conectar Stripe."""
        trip = await self._trip_repo.get_by_id(trip_id)
        ensure_trip_owner(trip, user_id)

        booking = await self._repo.get_by_trip_id(trip_id)
        if not booking:
            raise NotFoundError("No flight booked for this trip")
        if booking.status == "confirmed":
            return booking

        raw_offer = await self._fetch_raw_offer(booking.booking_token)
        passengers = raw_offer.get("passengers", [])
        if not passengers:
            raise ExternalServiceError("La oferta no tiene pasajeros asociados — búscala de nuevo")
        pax_id = passengers[0]["id"]

        order_body = {
            "data": {
                "selected_offers": [booking.booking_token],
                "passengers": [
                    {
                        "id": pax_id,
                        "given_name": data.given_name,
                        "family_name": data.family_name,
                        "born_on": data.born_on,
                        "email": data.email,
                        "phone_number": data.phone_number,
                        "title": data.title,
                        "gender": data.gender,
                    }
                ],
                "payments": [
                    {
                        "type": "balance",
                        "currency": raw_offer["total_currency"],
                        "amount": raw_offer["total_amount"],
                    }
                ],
            }
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.post(
                    f"{settings.DUFFEL_API_BASE_URL}/air/orders",
                    json=order_body,
                    headers={**_DUFFEL_HEADERS, "Content-Type": "application/json"},
                )
                response.raise_for_status()
            except httpx.HTTPError as e:
                raise ExternalServiceError(
                    f"No se pudo confirmar la reserva del vuelo (la oferta puede haber expirado, busca de nuevo): {e}"
                )

        order = response.json()["data"]
        booking.status = "confirmed"
        booking.duffel_order_id = order.get("id")
        booking.booking_reference = order.get("booking_reference")
        booking.passenger_given_name = data.given_name
        booking.passenger_family_name = data.family_name
        await booking.save()
        return booking

    async def get_flight(self, trip_id: str, user_id: str) -> FlightBooking:
        trip = await self._trip_repo.get_by_id(trip_id)
        ensure_trip_owner(trip, user_id)

        booking = await self._repo.get_by_trip_id(trip_id)
        if not booking:
            raise NotFoundError("No flight booked for this trip")
        return booking

    async def delete_flight(self, trip_id: str, user_id: str) -> None:
        booking = await self.get_flight(trip_id, user_id)
        await booking.delete()
