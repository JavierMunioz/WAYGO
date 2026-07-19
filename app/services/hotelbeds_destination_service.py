import hashlib
import logging
import time

import httpx

from app.core.config import settings
from app.models.hotelbeds_destination import HotelbedsDestination
from app.repositories.hotelbeds_destination_repository import HotelbedsDestinationRepository

logger = logging.getLogger(__name__)

_PAGE_SIZE = 100


def _hotelbeds_headers() -> dict:
    raw = f"{settings.HOTELBEDS_API_KEY}{settings.HOTELBEDS_SECRET}{int(time.time())}"
    return {
        "Api-key": settings.HOTELBEDS_API_KEY,
        "X-Signature": hashlib.sha256(raw.encode()).hexdigest(),
        "Accept": "application/json",
    }


class HotelbedsDestinationService:
    """Sincroniza el catálogo completo de destinos de Hotelbeds (ciudades,
    no aeropuertos — sus códigos no son IATA) para poder ofrecer
    autocompletado en la búsqueda de hospedaje sin llamar a la API externa
    en cada tecleo. Se corre una vez y de ahí en adelante queda cacheado."""

    def __init__(self, repo: HotelbedsDestinationRepository):
        self._repo = repo

    async def search(self, query: str, limit: int = 8) -> list[HotelbedsDestination]:
        if len(query.strip()) < 2:
            return []
        return await self._repo.search_by_name(query, limit=limit)

    async def sync_all(self) -> int:
        total_synced = 0
        page_from = 1
        async with httpx.AsyncClient(timeout=30.0) as client:
            while True:
                resp = await client.get(
                    f"{settings.HOTELBEDS_API_BASE_URL}/hotel-content-api/1.0/locations/destinations",
                    params={
                        "fields": "code,name,countryCode",
                        "language": "ENG",
                        "from": page_from,
                        "to": page_from + _PAGE_SIZE - 1,
                    },
                    headers=_hotelbeds_headers(),
                )
                resp.raise_for_status()
                data = resp.json()
                destinations = data.get("destinations", [])
                if not destinations:
                    break

                rows = [
                    {
                        "code": d["code"],
                        "name": d.get("name", {}).get("content", d["code"]),
                        "country_code": d.get("countryCode", ""),
                    }
                    for d in destinations
                    if d.get("code")
                ]
                total_synced += await self._repo.bulk_upsert(rows)

                total_available = data.get("total", 0)
                page_from += _PAGE_SIZE
                if page_from > total_available:
                    break

        logger.info("Hotelbeds destinations sync: %s registros", total_synced)
        return total_synced
