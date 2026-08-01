import pytest
from unittest.mock import patch, AsyncMock
from httpx import AsyncClient
from sqlalchemy import select

from app.models.user import User
from app.core.security import create_email_verification_token, hash_password

@pytest.fixture(autouse=True)
def mock_email_sending():
    with patch("app.services.auth_service.send_verification_email", new_callable=AsyncMock):
        yield

class TestRegister:
    async def test_register_new_user_succeeds(self, client: AsyncClient):
        response = await client.post("/api/v1/auth/register", json={
            "email": "newuser@example.com",
            "password": "SecurePass123",
        })

        assert response.status_code == 201
        data = response.json()
        assert data["email"] == "newuser@example.com"
        assert data["is_email_verified"] is False
        assert "hashed_password" not in data  

    async def test_register_with_weak_password_fails(self, client: AsyncClient):
        response = await client.post("/api/v1/auth/register", json={
            "email": "weak@example.com",
            "password": "short",
        })

        assert response.status_code == 422 

    async def test_register_duplicate_email_fails(self, client: AsyncClient):
        payload = {"email": "duplicate@example.com", "password": "SecurePass123"}

        first_response = await client.post("/api/v1/auth/register", json=payload)
        assert first_response.status_code == 201

        second_response = await client.post("/api/v1/auth/register", json=payload)
        assert second_response.status_code == 400


class TestLogin:
    async def test_login_unverified_user_fails(self, client: AsyncClient):
        await client.post("/api/v1/auth/register", json={
            "email": "unverified@example.com",
            "password": "SecurePass123",
        })

        response = await client.post("/api/v1/auth/login", json={
            "email": "unverified@example.com",
            "password": "SecurePass123",
        })

        assert response.status_code == 403

    async def test_login_with_wrong_password_fails(self, client: AsyncClient, db_session):
        await self._create_verified_user(db_session, "verified@example.com", "CorrectPass123")

        response = await client.post("/api/v1/auth/login", json={
            "email": "verified@example.com",
            "password": "WrongPassword",
        })

        assert response.status_code == 401

    async def test_login_verified_user_succeeds(self, client: AsyncClient, db_session):
        await self._create_verified_user(db_session, "verified2@example.com", "CorrectPass123")

        response = await client.post("/api/v1/auth/login", json={
            "email": "verified2@example.com",
            "password": "CorrectPass123",
        })

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"

    @staticmethod
    async def _create_verified_user(db_session, email: str, password: str) -> User:
        user = User(
            email=email,
            hashed_password=hash_password(password),
            is_email_verified=True,
        )
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)
        return user


class TestVerifyEmail:
    async def test_verify_email_with_valid_token_succeeds(self, client: AsyncClient, db_session):
        register_response = await client.post("/api/v1/auth/register", json={
            "email": "toverify@example.com",
            "password": "SecurePass123",
        })
        user_id = register_response.json()["id"]

        token = create_email_verification_token(user_id)
        response = await client.post("/api/v1/auth/verify-email", json={"token": token})

        assert response.status_code == 200
        assert response.json()["is_email_verified"] is True

    async def test_verify_email_with_invalid_token_fails(self, client: AsyncClient):
        response = await client.post("/api/v1/auth/verify-email", json={"token": "garbage-token"})

        assert response.status_code == 400


class TestRefreshAndLogout:
    async def test_refresh_rotates_token(self, client: AsyncClient, db_session):
        await TestLogin._create_verified_user(db_session, "refresh@example.com", "CorrectPass123")

        login_response = await client.post("/api/v1/auth/login", json={
            "email": "refresh@example.com",
            "password": "CorrectPass123",
        })
        old_refresh_token = login_response.json()["refresh_token"]

        refresh_response = await client.post("/api/v1/auth/refresh", json={
            "refresh_token": old_refresh_token,
        })
        assert refresh_response.status_code == 200
        new_refresh_token = refresh_response.json()["refresh_token"]

        assert new_refresh_token != old_refresh_token

        second_attempt = await client.post("/api/v1/auth/refresh", json={
            "refresh_token": old_refresh_token,
        })
        assert second_attempt.status_code == 401

    async def test_logout_revokes_refresh_token(self, client: AsyncClient, db_session):
        await TestLogin._create_verified_user(db_session, "logout@example.com", "CorrectPass123")

        login_response = await client.post("/api/v1/auth/login", json={
            "email": "logout@example.com",
            "password": "CorrectPass123",
        })
        tokens = login_response.json()
        access_token = tokens["access_token"]
        refresh_token = tokens["refresh_token"]

        logout_response = await client.post(
            "/api/v1/auth/logout",
            json={"refresh_token": refresh_token},
            headers={"Authorization": f"Bearer {access_token}"},
        )
        assert logout_response.status_code == 204

        refresh_attempt = await client.post("/api/v1/auth/refresh", json={
            "refresh_token": refresh_token,
        })
        assert refresh_attempt.status_code == 401