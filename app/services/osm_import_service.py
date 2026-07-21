import logging
import urllib.parse

import httpx

from app.core.config import settings
from app.core.constants import PlaceCategory
from app.models.place import Place
from app.repositories.place_repository import PlaceRepository
from app.utils.slug import slugify

logger = logging.getLogger(__name__)

_NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
_OVERPASS_URL = "https://overpass-api.de/api/interpreter"
_WIKIPEDIA_SUMMARY_URL = "https://{lang}.wikipedia.org/api/rest_v1/page/summary/{title}"
_WIKIMEDIA_FILEPATH_URL = "https://commons.wikimedia.org/wiki/Special:FilePath/{filename}"
_UNSPLASH_SEARCH_URL = "https://api.unsplash.com/search/photos"
_USER_AGENT = "WayGoApp/1.0 (viajes; contacto: waygobaqco@gmail.com)"
_MAX_PLACES_PER_CITY = 60
_SEARCH_RADIUS_METERS = 12_000
_TIMEOUT = httpx.Timeout(25.0, connect=10.0)

# Foto de stock genérica por categoría cuando no hay foto real — mismo query
# para toda una categoría, así que se puede cachear (evita gastar requests
# de Unsplash, cuyo free tier es de 50/hora).
_STOCK_QUERY_BY_CATEGORY: dict[PlaceCategory, str] = {
    PlaceCategory.MUSEUM: "museum interior",
    PlaceCategory.VIEWPOINT: "scenic viewpoint landscape",
    PlaceCategory.MONUMENT: "historic monument",
    PlaceCategory.ARCHAEOLOGICAL: "ancient ruins",
    PlaceCategory.PARK: "city park",
    PlaceCategory.NATURAL: "nature reserve",
    PlaceCategory.BEACH: "tropical beach",
    PlaceCategory.MOUNTAIN: "mountain peak",
    PlaceCategory.WATERFALL: "waterfall",
    PlaceCategory.RELIGIOUS: "church cathedral",
    PlaceCategory.RESTAURANT: "restaurant food",
    PlaceCategory.URBAN: "city street",
    PlaceCategory.OTHER: "travel destination",
}

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
        self._stock_cache: dict[str, str | None] = {}

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

    async def backfill_photos_for_city(self, city: str, country: str) -> int:
        """Para lugares ya importados sin foto (de antes de que existiera esta
        función) — reconsulta Overpass, cruza por nombre y rellena in-place
        sin tocar el _id (no rompe referencias de itinerarios existentes)."""
        existing = await self._repo.find_by_country_and_city(country, city, limit=200)
        missing = [p for p in existing if not p.cover_image]
        if not missing:
            return 0

        try:
            center = await self._geocode_center(city, country)
            elements = await self._fetch_overpass(center) if center else []
        except Exception:
            logger.exception("Backfill: Overpass falló para %s, %s", city, country)
            elements = []

        by_name = {e.get("tags", {}).get("name", "").strip().lower(): e.get("tags", {}) for e in elements}

        updated = 0
        for place in missing:
            tags = by_name.get(place.name.strip().lower())
            cover_image = await self._resolve_real_photo(tags) if tags else None
            source = "real"
            if cover_image is None:
                cover_image = await self._resolve_stock_photo(place.category)
                source = "stock"
            if cover_image:
                place.cover_image = cover_image
                place.cover_image_source = source
                await place.save()
                updated += 1

        logger.info("Backfill de fotos: %s/%s lugares actualizados en %s, %s", updated, len(missing), city, country)
        return updated

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

    async def _resolve_real_photo(self, tags: dict) -> str | None:
        """Intenta traer una foto AUTÉNTICA del lugar (nunca genérica) desde
        las referencias que el propio dato de OSM trae — en ese orden de
        confianza: archivo de Wikimedia Commons > imagen destacada del
        artículo de Wikipedia > URL directa en el tag `image`."""
        commons_file = tags.get("wikimedia_commons")
        if commons_file and commons_file.startswith("File:"):
            return _WIKIMEDIA_FILEPATH_URL.format(filename=urllib.parse.quote(commons_file[len("File:"):]))

        wikipedia_ref = tags.get("wikipedia")
        if wikipedia_ref and ":" in wikipedia_ref:
            lang, title = wikipedia_ref.split(":", 1)
            try:
                async with httpx.AsyncClient(headers={"User-Agent": _USER_AGENT}, timeout=_TIMEOUT) as client:
                    resp = await client.get(_WIKIPEDIA_SUMMARY_URL.format(lang=lang, title=urllib.parse.quote(title)))
                if resp.status_code == 200:
                    thumb = resp.json().get("thumbnail", {}).get("source")
                    if thumb:
                        return thumb
            except Exception:
                pass  # sin foto de esta fuente, seguimos con la siguiente

        image_tag = tags.get("image")
        if image_tag and image_tag.startswith("http"):
            return image_tag

        return None

    async def _resolve_stock_photo(self, category: PlaceCategory) -> str | None:
        """Foto de relleno genérica por categoría (Unsplash) — solo se usa
        cuando no hay ninguna foto real disponible. Cacheada por categoría
        en memoria durante la corrida del import para no gastar el límite
        de 50 requests/hora del free tier con la misma búsqueda repetida."""
        if not settings.UNSPLASH_ACCESS_KEY:
            return None

        query = _STOCK_QUERY_BY_CATEGORY.get(category, "travel destination")
        if query in self._stock_cache:
            return self._stock_cache[query]

        try:
            async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
                resp = await client.get(
                    _UNSPLASH_SEARCH_URL,
                    params={"query": query, "per_page": 1, "orientation": "landscape"},
                    headers={"Authorization": f"Client-ID {settings.UNSPLASH_ACCESS_KEY}"},
                )
            if resp.status_code == 200:
                results = resp.json().get("results", [])
                url = results[0]["urls"]["regular"] if results else None
            else:
                url = None
        except Exception:
            url = None

        self._stock_cache[query] = url
        return url

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

        cover_image = await self._resolve_real_photo(tags)
        cover_image_source = "real" if cover_image else None
        if cover_image is None:
            cover_image = await self._resolve_stock_photo(category)
            cover_image_source = "stock" if cover_image else None

        return Place(
            name=name,
            slug=slug,
            description=description,
            country=country,
            city=city,
            category=category,
            location={"type": "Point", "coordinates": [float(lon), float(lat)]},
            opening_hours=tags.get("opening_hours"),
            cover_image=cover_image,
            cover_image_source=cover_image_source,
        )
