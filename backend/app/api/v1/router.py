from fastapi import APIRouter

from app.api.v1 import auth, oauth, calculators, currency

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(auth.router)
api_router.include_router(oauth.router)
api_router.include_router(calculators.router)
api_router.include_router(currency.router)