import secrets

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_db
from app.utils.redis_client import redis_client
from app.services.oauth_service import OAuthService
from app.services.auth_service import AuthService

router = APIRouter(prefix="/oauth", tags=["oauth"])

STATE_TTL_SECONDS = 600  


#  Google

@router.get("/google/login")
async def google_login():
    """Генерує state (захист від CSRF), зберігає в Redis, редіректить на Google."""
    state = secrets.token_urlsafe(32)
    await redis_client.set(f"oauth_state:{state}", "google", ex=STATE_TTL_SECONDS)

    google_auth_url = (
        "https://accounts.google.com/o/oauth2/v2/auth"
        f"?client_id={settings.google_client_id}"
        f"&redirect_uri={settings.google_redirect_uri}"
        "&response_type=code"
        "&scope=openid%20email%20profile"
        f"&state={state}"
    )
    return RedirectResponse(url=google_auth_url)


@router.get("/google/callback")
async def google_callback(
    code: str,
    state: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    await _verify_state(state, expected_provider="google")

    oauth_service = OAuthService(db)
    auth_service = AuthService(db)

    user = await oauth_service.authenticate_google(code)
    tokens = await auth_service.issue_tokens(user, request)

    redirect_url = (
        f"{settings.frontend_url}/oauth-success"
        f"?access_token={tokens.access_token}&refresh_token={tokens.refresh_token}"
    )
    return RedirectResponse(url=redirect_url)


#  GitHub

@router.get("/github/login")
async def github_login():
    state = secrets.token_urlsafe(32)
    await redis_client.set(f"oauth_state:{state}", "github", ex=STATE_TTL_SECONDS)

    github_auth_url = (
        "https://github.com/login/oauth/authorize"
        f"?client_id={settings.github_client_id}"
        f"&redirect_uri={settings.github_redirect_uri}"
        "&scope=read:user%20user:email"
        f"&state={state}"
    )
    return RedirectResponse(url=github_auth_url)


@router.get("/github/callback")
async def github_callback(
    code: str,
    state: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    await _verify_state(state, expected_provider="github")

    oauth_service = OAuthService(db)
    auth_service = AuthService(db)

    user = await oauth_service.authenticate_github(code)
    tokens = await auth_service.issue_tokens(user, request)

    redirect_url = (
        f"{settings.frontend_url}/oauth-success"
        f"?access_token={tokens.access_token}&refresh_token={tokens.refresh_token}"
    )
    return RedirectResponse(url=redirect_url)


#  Спільна перевірка state (CSRF-захист)

async def _verify_state(state: str, expected_provider: str) -> None:
    key = f"oauth_state:{state}"
    stored_provider = await redis_client.get(key)

    if stored_provider is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired OAuth state",
        )

    if stored_provider != expected_provider:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="OAuth state provider mismatch",
        )

    await redis_client.delete(key)