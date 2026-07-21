import time

import httpx

from app.core.exceptions import ExternalServiceError

_RATES_URL = "https://open.er-api.com/v6/latest/USD"
_TIMEOUT = httpx.Timeout(10.0, connect=5.0)
_CACHE_TTL_SECONDS = 6 * 60 * 60  # la fuente actualiza 1 vez al día, 6h de caché es de sobra


class FxService:
    """Tasas de cambio con base USD — gratis, sin key, cacheadas en memoria
    del proceso para no golpear la API externa en cada request de precio."""

    _cached_rates: dict[str, float] | None = None
    _cached_at: float = 0.0
    _cached_updated_at: str | None = None

    async def get_rates(self) -> tuple[dict[str, float], str | None]:
        now = time.monotonic()
        if self._cached_rates is not None and (now - self._cached_at) < _CACHE_TTL_SECONDS:
            return self._cached_rates, self._cached_updated_at

        try:
            async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
                resp = await client.get(_RATES_URL)
                resp.raise_for_status()
                data = resp.json()
        except (httpx.HTTPError, ValueError) as exc:
            if self._cached_rates is not None:
                return self._cached_rates, self._cached_updated_at  # sirve caché vencida antes que fallar
            raise ExternalServiceError("No se pudieron obtener las tasas de cambio") from exc

        rates = {k: float(v) for k, v in data["rates"].items()}
        FxService._cached_rates = rates
        FxService._cached_at = now
        FxService._cached_updated_at = data.get("time_last_update_utc")
        return rates, self._cached_updated_at
