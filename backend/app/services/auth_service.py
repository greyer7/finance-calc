import asyncio
from datetime import datetime, timezone
from typing import Optional

from fastapi import HTTPException, status, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.models.refresh_token import RefreshToken
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserCreate
from app.schemas.auth import LoginRequest, TokenResponse
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    decode_access_token,
    generate_refresh_token,
    hash_token,
    get_refresh_token_expiry,
    create_email_verification_token,
    decode_email_verification_token,
)
from app.services.email_service import send_verification_email


class AuthService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_repo = UserRepository(db)

    #  Реєстрація

    async def register_user(self, data: UserCreate) -> User:
        existing_user = await self.user_repo.get_by_email(data.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )

        hashed = await asyncio.to_thread(hash_password, data.password)

        new_user = await self.user_repo.create(
            email=data.email,
            hashed_password=hashed,
            is_email_verified=False,
        )

        verification_token = create_email_verification_token(new_user.id)
        await send_verification_email(new_user.email, verification_token)

        return new_user

    #  Верифікація email

    async def verify_email(self, token: str) -> User:
        user_id = decode_email_verification_token(token)
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired verification token",
            )

        user = await self.user_repo.get_by_id(user_id)
        if user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        if user.is_email_verified:
            return user  

        return await self.user_repo.mark_email_verified(user)

    async def resend_verification_email(self, email: str) -> None:
        user = await self.user_repo.get_by_email(email)
        if user is None:
            return
        if user.is_email_verified:
            return

        verification_token = create_email_verification_token(user.id)
        await send_verification_email(user.email, verification_token)

    #  Логін (email + пароль)

    async def authenticate_user(self, data: LoginRequest) -> User:
        user = await self.user_repo.get_by_email(data.email)

        invalid_credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

        if user is None or user.hashed_password is None:
            raise invalid_credentials_exception

        is_valid = await asyncio.to_thread(verify_password, data.password, user.hashed_password)
        if not is_valid:
            raise invalid_credentials_exception

        if not user.is_email_verified:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Email not verified. Please check your inbox.",
            )

        return user

    #  Видача пари токенів (спільна для логіну, OAuth, register)

    async def issue_tokens(self, user: User, request: Optional[Request] = None) -> TokenResponse:
        access_token = create_access_token(user.id)

        raw_refresh_token = generate_refresh_token()
        refresh_record = RefreshToken(
            user_id=user.id,
            token_hash=hash_token(raw_refresh_token),
            expires_at=get_refresh_token_expiry(),
            user_agent=request.headers.get("user-agent") if request else None,
            ip_address=request.client.host if request and request.client else None,
        )
        self.db.add(refresh_record)
        await self.db.commit()

        return TokenResponse(access_token=access_token, refresh_token=raw_refresh_token)

    #  Refresh — з ротацією (старий токен одразу відкликається)

    async def refresh_tokens(self, raw_refresh_token: str, request: Optional[Request] = None) -> TokenResponse:
        token_hash = hash_token(raw_refresh_token)

        result = await self.db.execute(
            select(RefreshToken).where(RefreshToken.token_hash == token_hash)
        )
        record = result.scalar_one_or_none()

        invalid_token_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
        )

        if record is None:
            raise invalid_token_exception

        if record.is_revoked:
            
            await self.revoke_all_user_tokens(record.user_id)
            raise invalid_token_exception

        if record.expires_at < datetime.now(timezone.utc):
            raise invalid_token_exception

        record.is_revoked = True
        await self.db.commit()

        user = await self.user_repo.get_by_id(record.user_id)
        if user is None:
            raise invalid_token_exception

        return await self.issue_tokens(user, request)

    #  Logout

    async def revoke_refresh_token(self, raw_refresh_token: str) -> None:
        token_hash = hash_token(raw_refresh_token)
        result = await self.db.execute(
            select(RefreshToken).where(RefreshToken.token_hash == token_hash)
        )
        record = result.scalar_one_or_none()
        if record:
            record.is_revoked = True
            await self.db.commit()

    async def revoke_all_user_tokens(self, user_id: int) -> None:
        result = await self.db.execute(
            select(RefreshToken).where(RefreshToken.user_id == user_id, RefreshToken.is_revoked == False)
        )
        records = result.scalars().all()
        for record in records:
            record.is_revoked = True
        await self.db.commit()