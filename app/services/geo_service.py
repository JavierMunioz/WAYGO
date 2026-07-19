import httpx

_NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
_USER_AGENT = "WayGoApp/1.0 (viajes; contacto: waygobaqco@gmail.com)"
_TIMEOUT = httpx.Timeout(15.0, connect=8.0)


class GeoService:
    """Autocompletado de ciudad/país al crear un viaje — usa Nominatim
    (OpenStreetMap, gratis) para que el destino sea siempre un lugar real
    en vez de texto libre que el usuario puede escribir mal."""

    async def search_cities(self, query: str, limit: int = 8) -> list[dict]:
        if len(query.strip()) < 2:
            return []

        async with httpx.AsyncClient(headers={"User-Agent": _USER_AGENT}, timeout=_TIMEOUT) as client:
            resp = await client.get(
                _NOMINATIM_URL,
                params={"q": query.strip(), "format": "jsonv2", "addressdetails": 1, "limit": limit * 2},
            )
            resp.raise_for_status()
            results = resp.json()

        seen: set[tuple[str, str]] = set()
        suggestions: list[dict] = []
        for r in results:
            addr = r.get("address", {})
            city = addr.get("city") or addr.get("town") or addr.get("municipality") or addr.get("village")
            country = addr.get("country")
            country_code = (addr.get("country_code") or "").upper()
            if not city or not country:
                continue
            key = (city, country)
            if key in seen:
                continue
            seen.add(key)
            suggestions.append({"city": city, "country": country, "country_code": country_code})
            if len(suggestions) >= limit:
                break

        return suggestions
