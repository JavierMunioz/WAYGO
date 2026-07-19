import logging

import httpx

from app.core.constants import PlaceCategory
from app.models.place import Place
from app.repositories.place_repository import PlaceRepository
from app.utils.slug import slugify

logger = logging.getLogger(__name__)

_NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
_OVERPASS_URL = "https://overpass-api.de/api/interpreter"
_USER_AGENT = "WayGoApp/1.0 (viajes; contacto: waygobaqco@gmail.com)"
_MAX_PLACES_PER_CITY = 60
_SEARCH_RADIUS_METERS = 12_000
_TIMEOUT = httpx.Timeout(25.0, connect=10.0)

# Mapea etiquetas de OpenStreetMap a nuestras categorías — la primera que
# haga match sobre los tags del elemento gana.
_OSM_TAG_CATEGORY_MAP: list[tuple[str, str, PlaceCategory]] = [
    ("tourism", "museum", PlaceCategory.MUSEUM),
    ("tourism", "gallery", PlaceCategory.MUSEUM),
    ("tourism", "viewpoint", PlaceCategory.VIEWPOINT),
    ("tourism", "attraction", PlaceCategory.URBAN),
    ("tourism", "zoo", PlaceCategory.OTHER),
    ("tourism", "theme_park", PlaceCategory.OTHER),
    ("tourism", "aquarium", PlaceCategory.OTHER),
    ("historic", "monument", PlaceCategory.MONUMENT),
    ("historic", "memorial", PlaceCategory.MONUMENT),
    ("historic", "castle", PlaceCategory.MONUMENT),
    ("historic", "fort", PlaceCategory.MONUMENT),
    ("historic", "archaeological_site", PlaceCategory.ARCHAEOLOGICAL),
    ("historic", "ruins", PlaceCategory.ARCHAEOLOGICAL),
    ("leisure", "park", PlaceCategory.PARK),
    ("leisure", "garden", PlaceCategory.PARK),
    ("leisure", "nature_reserve", PlaceCategory.NATURAL),
    ("natural", "beach", PlaceCategory.BEACH),
    ("natural", "peak", PlaceCategory.MOUNTAIN),
    ("natural", "waterfall", PlaceCategory.WATERFALL),
    ("waterway", "waterfall", PlaceCategory.WATERFALL),
    ("amenity", "place_of_worship", PlaceCategory.RELIGIOUS),
    ("amenity", "restaurant", PlaceCategory.RESTAURANT),
]

# Consulta Overpass: un bloque node/way por cada tag que nos interesa, todos
# dentro de un radio fijo alrededor del centro de la ciudad (más confiable
# que el bounding box de Nominatim, que a veces cubre todo el departamento).
_OVERPASS_TAG_FILTERS = "".join(
    f'\n  node(around:{{radius}},{{lat}},{{lon}})["{key}"="{value}"];'
    f'\n  way(around:{{radius}},{{lat}},{{lon}})["{key}"="{value}"];'
    for key, value, _ in _OSM_TAG_CATEGORY_MAP
)


def _category_for_tags(tags: dict) -> PlaceCategory | None:
    for key, value, category in _OSM_TAG_CATEGORY_MAP:
        if tags.get(key) == value:
            return category
    return None


class OsmImportService:
    """Importa lugares reales desde OpenStreetMap (gratis, sin costo por
    request) para ciudades que todavía no tienen lugares curados en la app.
    Se dispara una sola vez por ciudad — los resultados quedan cacheados en
    Mongo, así que el costo de red solo se paga la primera vez que alguien
    planea un viaje a esa ciudad."""

    def __init__(self, place_repo: PlaceRepository):
        self._repo = place_repo

    async def import_places_for_city(self, city: str, country: str) -> int:
        try:
            center = await self._geocode_center(city, country)
        except Exception:
            logger.exception("OSM geocode falló para %s, %s", city, country)
            return 0
        if center is None:
            return 0

        try:
            elements = await self._fetch_overpass(center)
        except Exception:
            logger.exception("Overpass falló para %s, %s", city, country)
            return 0

        inserted = 0
        for el in elements:
            if inserted >= _MAX_PLACES_PER_CITY:
                break
            place = await self._element_to_place(el, city, country)
            if place is None:
                continue
            await place.save()
            inserted += 1

        logger.info("OSM import: %s lugares nuevos para %s, %s", inserted, city, country)
        return inserted

    async def _geocode_center(self, city: str, country: str) -> tuple[float, float] | None:
        async with httpx.AsyncClient(headers={"User-Agent": _USER_AGENT}, timeout=_TIMEOUT) as client:
            resp = await client.get(
                _NOMINATIM_URL,
                params={"city": city, "country": country, "format": "json", "limit": 1},
            )
            resp.raise_for_status()
            results = resp.json()
        if not results:
            return None
        return float(results[0]["lat"]), float(results[0]["lon"])

    async def _fetch_overpass(self, center: tuple[float, float]) -> list[dict]:
        lat, lon = center
        filters = _OVERPASS_TAG_FILTERS.format(radius=_SEARCH_RADIUS_METERS, lat=lat, lon=lon)
        query = f"[out:json][timeout:25];\n({filters}\n);\nout center tags;"
        async with httpx.AsyncClient(headers={"User-Agent": _USER_AGENT}, timeout=_TIMEOUT) as client:
            resp = await client.post(_OVERPASS_URL, data={"data": query})
            resp.raise_for_status()
            data = resp.json()
        return data.get("elements", [])

    async def _element_to_place(self, el: dict, city: str, country: str) -> Place | None:
        tags = el.get("tags", {})
        name = tags.get("name")
        if not name:
            return None

        category = _category_for_tags(tags)
        if category is None:
            return None

        lat = el.get("lat") or (el.get("center") or {}).get("lat")
        lon = el.get("lon") or (el.get("center") or {}).get("lon")
        if lat is None or lon is None:
            return None

        base_slug = slugify(f"{name}-{city}")
        slug = base_slug
        counter = 1
        while await self._repo.get_by_slug(slug):
            slug = f"{base_slug}-{counter}"
            counter += 1

        description = tags.get("description") or f"{name} — lugar de interés en {city}."

        return Place(
            name=name,
            slug=slug,
            description=description,
            country=country,
            city=city,
            category=category,
            location={"type": "Point", "coordinates": [float(lon), float(lat)]},
            opening_hours=tags.get("opening_hours"),
        )
