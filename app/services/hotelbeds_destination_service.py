import asyncio
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

    async def _get_page_with_retry(self, client: httpx.AsyncClient, page_from: int) -> httpx.Response:
        for attempt in range(5):
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
            if resp.status_code in (403, 429) and attempt < 4:
                wait = 2 ** attempt  # 1s, 2s, 4s, 8s
                logger.warning("Hotelbeds %s en página %s, reintentando en %ss", resp.status_code, page_from, wait)
                await asyncio.sleep(wait)
                continue
            resp.raise_for_status()
            return resp
        resp.raise_for_status()
        return resp

    async def sync_all(self, start_from: int = 1) -> int:
        total_synced = 0
        page_from = start_from
        async with httpx.AsyncClient(timeout=30.0) as client:
            while True:
                resp = await self._get_page_with_retry(client, page_from)
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
                logger.info("Hotelbeds destinations sync: página desde %s (%s registros)", page_from, len(rows))

                await asyncio.sleep(0.4)  # respeta el rate limit de la API test

                total_available = data.get("total", 0)
                page_from += _PAGE_SIZE
                if page_from > total_available:
                    break

        logger.info("Hotelbeds destinations sync: %s registros", total_synced)
        return total_synced
