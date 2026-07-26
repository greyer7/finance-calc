from typing import Optional

import httpx
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models.user import User
from app.repositories.user_repository import UserRepository

# --- Google OAuth2 endpoints ---
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v3/userinfo"

# --- GitHub OAuth2 endpoints ---
GITHUB_TOKEN_URL = "https://github.com/login/oauth/access_token"
GITHUB_USERINFO_URL = "https://api.github.com/user"
GITHUB_EMAILS_URL = "https://api.github.com/user/emails"


class OAuthService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_repo = UserRepository(db)

    #  Google

    async def authenticate_google(self, code: str) -> User:
        async with httpx.AsyncClient() as client:
            token_response = await client.post(
                GOOGLE_TOKEN_URL,
                data={
                    "code": code,
                    "client_id": settings.google_client_id,
                    "client_secret": settings.google_client_secret,
                    "redirect_uri": settings.google_redirect_uri,
                    "grant_type": "authorization_code",
                },
            )

        if token_response.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Failed to exchange Google authorization code",
            )

        google_access_token = token_response.json()["access_token"]

        async with httpx.AsyncClient() as client:
            userinfo_response = await client.get(
                GOOGLE_USERINFO_URL,
                headers={"Authorization": f"Bearer {google_access_token}"},
            )

        if userinfo_response.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Failed to fetch Google user info",
            )

        userinfo = userinfo_response.json()
        google_id = userinfo["sub"]
        email = userinfo["email"]
        email_verified = userinfo.get("email_verified", False)

        return await self._get_or_create_oauth_user(
            provider="google",
            oauth_id=google_id,
            email=email,
            email_verified=email_verified,
        )

    #  GitHub

    async def authenticate_github(self, code: str) -> User:
        async with httpx.AsyncClient() as client:
            token_response = await client.post(
                GITHUB_TOKEN_URL,
                data={
                    "code": code,
                    "client_id": settings.github_client_id,
                    "client_secret": settings.github_client_secret,
                    "redirect_uri": settings.github_redirect_uri,
                },
                headers={"Accept": "application/json"},
            )

        if token_response.status_code != 200 or "access_token" not in token_response.json():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Failed to exchange GitHub authorization code",
            )

        github_access_token = token_response.json()["access_token"]
        headers = {
            "Authorization": f"Bearer {github_access_token}",
            "Accept": "application/json",
        }

        async with httpx.AsyncClient() as client:
            userinfo_response = await client.get(GITHUB_USERINFO_URL, headers=headers)

        if userinfo_response.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Failed to fetch GitHub user info",
            )

        userinfo = userinfo_response.json()
        github_id = str(userinfo["id"])

        
        email = userinfo.get("email")
        if email is None:
            email = await self._fetch_github_primary_email(headers)

        return await self._get_or_create_oauth_user(
            provider="github",
            oauth_id=github_id,
            email=email,
            email_verified=True,  
        )

    async def _fetch_github_primary_email(self, headers: dict) -> str:
        async with httpx.AsyncClient() as client:
            response = await client.get(GITHUB_EMAILS_URL, headers=headers)

        if response.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Failed to fetch GitHub email",
            )

        emails = response.json()
        primary = next((e for e in emails if e.get("primary") and e.get("verified")), None)

        if primary is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No verified primary email found on GitHub account",
            )

        return primary["email"]

    #  Спільна логіка: знайти або створити юзера за OAuth-даними

    async def _get_or_create_oauth_user(
        self,
        provider: str,
        oauth_id: str,
        email: str,
        email_verified: bool,
    ) -> User:
        existing_by_oauth = await self.user_repo.get_by_oauth(provider, oauth_id)
        if existing_by_oauth:
            return existing_by_oauth

       
        existing_by_email = await self.user_repo.get_by_email(email)
        if existing_by_email:
            
            return await self.user_repo.update(
                existing_by_email,
                oauth_provider=provider,
                oauth_id=oauth_id,
            )

        return await self.user_repo.create(
            email=email,
            hashed_password=None,
            oauth_provider=provider,
            oauth_id=oauth_id,
            is_email_verified=email_verified,
        )