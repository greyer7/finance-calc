from typing import Optional

from pydantic import BaseModel, EmailStr


# --- Вхідна схема: логін через email+пароль ---
class LoginRequest(BaseModel):
    email: EmailStr
    password: str


# --- Вихідна схема: пара токенів після успішного логіну/реєстрації/refresh ---
class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


# --- Вхідна схема: запит на оновлення access token ---
class RefreshTokenRequest(BaseModel):
    refresh_token: str


# --- Внутрішня схема: те, що "зашито" всередині JWT access token ---
class TokenPayload(BaseModel):
    sub: str          
    exp: int          
    type: str = "access" 


# --- Вхідна схема: підтвердження email за токеном з листа ---
class EmailVerificationRequest(BaseModel):
    token: str


# --- Вхідна схема: запит повторного листа верифікації (якщо перший загубився/протух) ---
class ResendVerificationRequest(BaseModel):
    email: EmailStr


# --- Вхідна схема: callback від Google/GitHub OAuth (код авторизації) ---
class OAuthCallbackRequest(BaseModel):
    code: str
    state: Optional[str] = None  