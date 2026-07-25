from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, ConfigDict, field_validator


class UserBase(BaseModel):
    email: EmailStr
    default_currency: str = "USD"


class UserCreate(BaseModel):
    email: EmailStr
    password: str

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str) -> str:
        if len(value) < 8:
            raise ValueError("Password must be at least 8 characters long")
        if not any(char.isdigit() for char in value):
            raise ValueError("Password must contain at least one digit")
        if not any(char.isupper() for char in value):
            raise ValueError("Password must contain at least one uppercase letter")
        return value


class UserUpdate(BaseModel):
    default_currency: Optional[str] = None


class UserResponse(UserBase):
    model_config = ConfigDict(from_attributes=True)  

    id: int
    is_email_verified: bool
    oauth_provider: Optional[str] = None
    created_at: datetime


class UserInDB(UserResponse):
    hashed_password: Optional[str] = None