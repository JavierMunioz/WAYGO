from datetime import UTC, datetime, timedelta

from app.core.constants import PlaceCategory, TripAvailability
from app.core.exceptions import AlreadyExistsError, NotFoundError
from app.models.itinerary import Itinerary, ItineraryBlock, ItineraryDay
from app.models.place import Place
from app.models.trip import Trip
from app.repositories.itinerary_repository import ItineraryRepository
from app.repositories.place_repository import PlaceRepository
from app.repositories.trip_repository import TripRepository
from app.schemas.itinerary import UpdateItineraryRequest
from app.utils.geo import haversine_distance
from app.utils.ownership import ensure_trip_owner

# Curación por reglas: sin IA, sin costo externo. Usa lo que ya tenemos
# (rating de la comunidad, categoría del lugar, cercanía geográfica).
# Un viaje "tiempo parcial" (el usuario tiene otros compromisos, ej. trabajo)
# recibe menos bloques y solo en horario nocturno.
_FULL_TIME_SLOTS = [("09:00", "11:00"), ("12:30", "14:30"), ("16:00", "18:00")]
_PART_TIME_SLOTS = [("18:00", "20:00")]

_INTEREST_CATEGORY_MAP: dict[str, list[PlaceCategory]] = {
    "playa": [PlaceCategory.BEACH],
    "montana": [PlaceCategory.MOUNTAIN],
    "montaña": [PlaceCategory.MOUNTAIN],
    "historia": [PlaceCategory.MONUMENT, PlaceCategory.ARCHAEOLOGICAL, PlaceCategory.RELIGIOUS],
    "museo": [PlaceCategory.MUSEUM],
    "museos": [PlaceCategory.MUSEUM],
    "gastronomia": [PlaceCategory.RESTAURANT],
    "gastronomía": [PlaceCategory.RESTAURANT],
    "comida": [PlaceCategory.RESTAURANT],
    "naturaleza": [PlaceCategory.NATURAL, PlaceCategory.PARK, PlaceCategory.WATERFALL],
    "arquitectura": [PlaceCategory.URBAN, PlaceCategory.MONUMENT],
    "religion": [PlaceCategory.RELIGIOUS],
    "religión": [PlaceCategory.RELIGIOUS],
    "miradores": [PlaceCategory.VIEWPOINT],
    "vistas": [PlaceCategory.VIEWPOINT],
    "arte": [PlaceCategory.MUSEUM, PlaceCategory.URBAN],
}


class ItineraryService:
    def __init__(
        self,
        itinerary_repo: ItineraryRepository,
        trip_repo: TripRepository,
        place_repo: PlaceRepository,
    ):
        self._repo = itinerary_repo
        self._trip_repo = trip_repo
        self._place_repo = place_repo

    async def generate_for_trip(self, trip_id: str, user_id: str) -> Itinerary:
        trip = await self._trip_repo.get_by_id(trip_id)
        ensure_trip_owner(trip, user_id)

        existing = await self._repo.get_by_trip_id(trip_id)
        if existing:
            raise AlreadyExistsError("Itinerary already exists for this trip")

        days = [
            ItineraryDay(day_number=i + 1, date=trip.start_date + timedelta(days=i))
            for i in range(trip.days)
        ]

        candidates = await self._curate_places(trip)
        if candidates:
            days = self._distribute_places(days, candidates, trip.availability)

        itinerary = Itinerary(trip_id=trip_id, user_id=user_id, days=days)
        await itinerary.save()
        return itinerary

    async def get_by_trip(self, trip_id: str, user_id: str) -> Itinerary:
        trip = await self._trip_repo.get_by_id(trip_id)
        ensure_trip_owner(trip, user_id)

        itinerary = await self._repo.get_by_trip_id(trip_id)
        if not itinerary:
            raise NotFoundError("Itinerary not found for this trip")
        return itinerary

    async def update_itinerary(self, trip_id: str, user_id: str, data: UpdateItineraryRequest) -> Itinerary:
        itinerary = await self.get_by_trip(trip_id, user_id)
        itinerary.days = [ItineraryDay(**d.model_dump()) for d in data.days]
        itinerary.updated_at = datetime.now(UTC)
        await itinerary.save()
        return itinerary

    async def delete_itinerary(self, trip_id: str, user_id: str) -> None:
        itinerary = await self.get_by_trip(trip_id, user_id)
        await itinerary.delete()

    async def _curate_places(self, trip: Trip) -> list[Place]:
        """Places del destino, ordenados por qué tan bien encajan con el viaje."""
        places = await self._place_repo.find_by_country_and_city(
            trip.destination_country, trip.destination_city, limit=200
        )
        if not places:
            return []

        wanted_categories: set[PlaceCategory] = set()
        for interest in trip.interests:
            for keyword, categories in _INTEREST_CATEGORY_MAP.items():
                if keyword in interest.lower():
                    wanted_categories.update(categories)

        def score(place: Place) -> float:
            interest_bonus = 10.0 if (wanted_categories and place.category in wanted_categories) else 0.0
            rating_bonus = place.average_rating * 2
            popularity_bonus = min(place.total_visits, 50) * 0.02
            return interest_bonus + rating_bonus + popularity_bonus

        return sorted(places, key=score, reverse=True)

    def _distribute_places(
        self, days: list[ItineraryDay], candidates: list[Place], availability: TripAvailability
    ) -> list[ItineraryDay]:
        time_slots = _PART_TIME_SLOTS if availability == TripAvailability.PART_TIME else _FULL_TIME_SLOTS
        max_per_day = len(time_slots)
        remaining = list(candidates)

        for day in days:
            if not remaining:
                break

            picks = remaining[:max_per_day]
            remaining = remaining[max_per_day:]
            ordered = self._order_by_proximity(picks)

            blocks = []
            for i, place in enumerate(ordered):
                start, end = time_slots[i] if i < len(time_slots) else (None, None)
                blocks.append(
                    ItineraryBlock(
                        order=i,
                        start_time=start,
                        end_time=end,
                        place_id=str(place.id),
                        title=place.name,
                        notes=place.fun_fact,
                        is_free_time=False,
                    )
                )
            day.blocks = blocks

        return days

    @staticmethod
    def _order_by_proximity(places: list[Place]) -> list[Place]:
        """Reordena por vecino más cercano — ruta corta dentro del día (greedy)."""
        if len(places) <= 1:
            return places

        remaining = list(places)
        route = [remaining.pop(0)]
        while remaining:
            last = route[-1]
            last_lng, last_lat = last.location["coordinates"]
            nearest = min(
                remaining,
                key=lambda p: haversine_distance(last_lat, last_lng, p.location["coordinates"][1], p.location["coordinates"][0]),
            )
            route.append(nearest)
            remaining.remove(nearest)
        return route
