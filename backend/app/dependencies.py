from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.core.security import decode_access_token
from app.repositories.user_repository import UserRepository
from app.models.user import User


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception

    user_id: int | None = payload.sub
    if user_id is None:
        raise credentials_exception

    user_repo = UserRepository(db)
    user = await user_repo.get_by_id(int(user_id))

    if user is None:
        raise credentials_exception

    return user


async def get_current_verified_user(
    current_user: User = Depends(get_current_user),
) -> User:
    
    if not current_user.is_email_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email not verified. Please check your inbox.",
        )
    return current_user