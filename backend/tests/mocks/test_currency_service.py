import json

import pytest
import respx
import httpx

from app.services.currency_service import CurrencyService
from app.config import settings


@pytest.fixture(autouse=True)
async def clear_redis_cache():
    from app.utils.redis_client import redis_client

    await redis_client.flushdb()
    yield
    await redis_client.flushdb()


class TestCurrencyServiceWithMockedAPI:
    @respx.mock
    async def test_get_rates_success_caches_result(self):
        mock_url = f"{settings.exchange_rate_api_base_url}/{settings.exchange_rate_api_key}/latest/USD"
        respx.get(mock_url).mock(
            return_value=httpx.Response(200, json={
                "result": "success",
                "conversion_rates": {"UAH": 41.5, "EUR": 0.92},
            })
        )

        service = CurrencyService()
        rates = await service.get_rates("USD")

        assert rates == {"UAH": 41.5, "EUR": 0.92}

    @respx.mock
    async def test_get_rates_uses_cache_on_second_call(self):
        mock_url = f"{settings.exchange_rate_api_base_url}/{settings.exchange_rate_api_key}/latest/USD"
        route = respx.get(mock_url).mock(
            return_value=httpx.Response(200, json={
                "result": "success",
                "conversion_rates": {"UAH": 41.5},
            })
        )

        service = CurrencyService()
        await service.get_rates("USD")
        await service.get_rates("USD")  
        assert route.call_count == 1

    @respx.mock
    async def test_force_refresh_ignores_cache(self):
        mock_url = f"{settings.exchange_rate_api_base_url}/{settings.exchange_rate_api_key}/latest/USD"
        route = respx.get(mock_url).mock(
            return_value=httpx.Response(200, json={
                "result": "success",
                "conversion_rates": {"UAH": 41.5},
            })
        )

        service = CurrencyService()
        await service.get_rates("USD")
        await service.get_rates("USD", force_refresh=True) 

        assert route.call_count == 2

    @respx.mock
    async def test_external_api_down_returns_none_without_cache(self):
        mock_url = f"{settings.exchange_rate_api_base_url}/{settings.exchange_rate_api_key}/latest/USD"
        respx.get(mock_url).mock(return_value=httpx.Response(500))

        service = CurrencyService()
        rates = await service.get_rates("USD")

        assert rates is None

    @respx.mock
    async def test_external_api_down_falls_back_to_stale_cache(self):
        mock_url = f"{settings.exchange_rate_api_base_url}/{settings.exchange_rate_api_key}/latest/USD"

        route = respx.get(mock_url).mock(
            return_value=httpx.Response(200, json={
                "result": "success",
                "conversion_rates": {"UAH": 41.5},
            })
        )
        service = CurrencyService()
        await service.get_rates("USD")

        route.mock(return_value=httpx.Response(500))
        rates = await service.get_rates("USD", force_refresh=True)

        assert rates == {"UAH": 41.5}

    @respx.mock
    async def test_api_error_result_field_returns_none(self):
        mock_url = f"{settings.exchange_rate_api_base_url}/{settings.exchange_rate_api_key}/latest/USD"
        respx.get(mock_url).mock(
            return_value=httpx.Response(200, json={"result": "error", "error-type": "invalid-key"})
        )

        service = CurrencyService()
        rates = await service.get_rates("USD")

        assert rates is None

    @respx.mock
    async def test_network_timeout_returns_none(self):
        mock_url = f"{settings.exchange_rate_api_base_url}/{settings.exchange_rate_api_key}/latest/USD"
        respx.get(mock_url).mock(side_effect=httpx.TimeoutException("Connection timed out"))

        service = CurrencyService()
        rates = await service.get_rates("USD")

        assert rates is None


class TestCurrencyConversion:
    @respx.mock
    async def test_convert_same_currency_returns_same_amount(self):
        service = CurrencyService()
        result = await service.convert(100, "USD", "USD")

        assert result == 100

    @respx.mock
    async def test_convert_calculates_correctly(self):
        mock_url = f"{settings.exchange_rate_api_base_url}/{settings.exchange_rate_api_key}/latest/USD"
        respx.get(mock_url).mock(
            return_value=httpx.Response(200, json={
                "result": "success",
                "conversion_rates": {"UAH": 41.5},
            })
        )

        service = CurrencyService()
        result = await service.convert(100, "USD", "UAH")

        assert result == 4150.0

    @respx.mock
    async def test_convert_unknown_currency_returns_none(self):
        mock_url = f"{settings.exchange_rate_api_base_url}/{settings.exchange_rate_api_key}/latest/USD"
        respx.get(mock_url).mock(
            return_value=httpx.Response(200, json={
                "result": "success",
                "conversion_rates": {"UAH": 41.5},
            })
        )

        service = CurrencyService()
        result = await service.convert(100, "USD", "XYZ")

        assert result is None