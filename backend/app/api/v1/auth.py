from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse
from app.schemas.auth import (
    LoginRequest,
    TokenResponse,
    RefreshTokenRequest,
    EmailVerificationRequest,
    ResendVerificationRequest,
)
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(data: UserCreate, db: AsyncSession = Depends(get_db)):
    auth_service = AuthService(db)
    user = await auth_service.register_user(data)
    return user


@router.post("/verify-email", response_model=UserResponse)
async def verify_email(data: EmailVerificationRequest, db: AsyncSession = Depends(get_db)):
    auth_service = AuthService(db)
    user = await auth_service.verify_email(data.token)
    return user


@router.post("/resend-verification", status_code=status.HTTP_204_NO_CONTENT)
async def resend_verification(data: ResendVerificationRequest, db: AsyncSession = Depends(get_db)):
    auth_service = AuthService(db)
    await auth_service.resend_verification_email(data.email)
    return None


@router.post("/login", response_model=TokenResponse)
async def login(data: LoginRequest, request: Request, db: AsyncSession = Depends(get_db)):
    auth_service = AuthService(db)
    user = await auth_service.authenticate_user(data)
    return await auth_service.issue_tokens(user, request)


@router.post("/refresh", response_model=TokenResponse)
async def refresh(data: RefreshTokenRequest, request: Request, db: AsyncSession = Depends(get_db)):
    auth_service = AuthService(db)
    return await auth_service.refresh_tokens(data.refresh_token, request)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    data: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    auth_service = AuthService(db)
    await auth_service.revoke_refresh_token(data.refresh_token)
    return None


@router.post("/logout-all", status_code=status.HTTP_204_NO_CONTENT)
async def logout_all(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    auth_service = AuthService(db)
    await auth_service.revoke_all_user_tokens(current_user.id)
    return None


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user