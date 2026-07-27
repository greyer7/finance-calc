import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.config import settings
from app.services.currency_service import CurrencyService

logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler()

TRACKED_CURRENCIES = ["USD", "EUR", "UAH"]


async def refresh_currency_rates_job() -> None:
    """Фоново оновлює курси валют у Redis, ігноруючи наявний кеш."""
    currency_service = CurrencyService()

    for base_currency in TRACKED_CURRENCIES:
        rates = await currency_service.get_rates(base_currency=base_currency, force_refresh=True)
        if rates is None:
            logger.warning(f"Failed to refresh currency rates for {base_currency}")
        else:
            logger.info(f"Currency rates refreshed for {base_currency}")


def start_scheduler() -> None:
    scheduler.add_job(
        refresh_currency_rates_job,
        trigger="interval",
        minutes=settings.currency_refresh_interval_minutes,
        id="refresh_currency_rates",
        replace_existing=True,
    )
    scheduler.start()
    logger.info(
        f"Currency refresh scheduler started (every {settings.currency_refresh_interval_minutes} minutes)"
    )