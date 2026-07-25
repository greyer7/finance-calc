from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.schemas.user import UserCreate


class UserRepository:
   

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, user_id: int) -> Optional[User]:
        result = await self.db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> Optional[User]:
        result = await self.db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def get_by_oauth(self, provider: str, oauth_id: str) -> Optional[User]:
        result = await self.db.execute(
            select(User).where(
                User.oauth_provider == provider,
                User.oauth_id == oauth_id,
            )
        )
        return result.scalar_one_or_none()

    async def create(self, email: str, hashed_password: Optional[str] = None,
                      oauth_provider: Optional[str] = None,
                      oauth_id: Optional[str] = None,
                      is_email_verified: bool = False) -> User:
        user = User(
            email=email,
            hashed_password=hashed_password,
            oauth_provider=oauth_provider,
            oauth_id=oauth_id,
            is_email_verified=is_email_verified,
        )
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)  
        return user

    async def update(self, user: User, **fields) -> User:
        for key, value in fields.items():
            setattr(user, key, value)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def mark_email_verified(self, user: User) -> User:
        user.is_email_verified = True
        await self.db.commit()
        await self.db.refresh(user)
        return user