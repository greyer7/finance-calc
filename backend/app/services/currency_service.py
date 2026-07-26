import json
from typing import Optional

import httpx

from app.config import settings
from app.utils.redis_client import redis_client

CACHE_KEY_PREFIX = "currency_rates"
CACHE_TTL_SECONDS = 3600  


class CurrencyService:
    async def get_rates(self, base_currency: str = "USD", force_refresh: bool = False) -> Optional[dict]:
        
        cache_key = f"{CACHE_KEY_PREFIX}:{base_currency}"

        if not force_refresh:
            cached = await redis_client.get(cache_key)
            if cached:
                return json.loads(cached)

        fresh_rates = await self._fetch_from_external_api(base_currency)

        if fresh_rates is not None:
            await redis_client.set(cache_key, json.dumps(fresh_rates), ex=CACHE_TTL_SECONDS)
            return fresh_rates

   
        cached = await redis_client.get(cache_key)
        if cached:
            return json.loads(cached)

        return None

    async def _fetch_from_external_api(self, base_currency: str) -> Optional[dict]:
        url = f"{settings.exchange_rate_api_base_url}/{settings.exchange_rate_api_key}/latest/{base_currency}"

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(url)
        except httpx.RequestError:
            return None

        if response.status_code != 200:
            return None

        data = response.json()

        if data.get("result") != "success":
            return None

        return data.get("conversion_rates")

    async def invalidate_cache(self, base_currency: str) -> None:
        cache_key = f"{CACHE_KEY_PREFIX}:{base_currency}"
        await redis_client.delete(cache_key)

    async def convert(self, amount: float, from_currency: str, to_currency: str) -> Optional[float]:
        if from_currency == to_currency:
            return amount

        rates = await self.get_rates(base_currency=from_currency)
        if rates is None or to_currency not in rates:
            return None

        return round(amount * rates[to_currency], 2)