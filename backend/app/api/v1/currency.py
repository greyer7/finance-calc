from fastapi import APIRouter, Depends, HTTPException, Request, status

from app.dependencies import get_current_user
from app.models.user import User
from app.services.currency_service import CurrencyService
from app.core.limiter import limiter

router = APIRouter(prefix="/currency", tags=["currency"])


@router.get("/rates")
async def get_rates(base: str = "USD"):
    currency_service = CurrencyService()
    rates = await currency_service.get_rates(base_currency=base.upper())

    if rates is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Currency rates temporarily unavailable",
        )

    return {"base": base.upper(), "rates": rates}


@router.get("/convert")
async def convert_currency(amount: float, from_currency: str, to_currency: str):
    currency_service = CurrencyService()
    converted = await currency_service.convert(
        amount=amount,
        from_currency=from_currency.upper(),
        to_currency=to_currency.upper(),
    )

    if converted is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unable to convert between the specified currencies",
        )

    return {
        "amount": amount,
        "from_currency": from_currency.upper(),
        "to_currency": to_currency.upper(),
        "converted_amount": converted,
    }


@router.post("/refresh", status_code=status.HTTP_204_NO_CONTENT)
@limiter.limit("3/minute")
async def force_refresh_rates(
    request: Request,
    base: str = "USD",
    current_user: User = Depends(get_current_user),
):
    currency_service = CurrencyService()
    await currency_service.invalidate_cache(base.upper())
    await currency_service.get_rates(base_currency=base.upper(), force_refresh=True)
    return None