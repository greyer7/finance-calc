import time

import pytest
from jose import jwt

from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    decode_access_token,
    generate_refresh_token,
    hash_token,
    create_email_verification_token,
    decode_email_verification_token,
)
from app.config import settings


class TestPasswordHashing:
    def test_hash_password_returns_different_string(self):
        plain = "SecurePass123"
        hashed = hash_password(plain)

        assert hashed != plain

    def test_verify_correct_password_succeeds(self):
        plain = "SecurePass123"
        hashed = hash_password(plain)

        assert verify_password(plain, hashed) is True

    def test_verify_incorrect_password_fails(self):
        hashed = hash_password("SecurePass123")

        assert verify_password("WrongPassword", hashed) is False

    def test_same_password_produces_different_hashes(self):
        hash1 = hash_password("SecurePass123")
        hash2 = hash_password("SecurePass123")

        assert hash1 != hash2
        assert verify_password("SecurePass123", hash1) is True
        assert verify_password("SecurePass123", hash2) is True


class TestAccessToken:
    def test_create_and_decode_access_token(self):
        token = create_access_token(user_id=42)
        payload = decode_access_token(token)

        assert payload is not None
        assert payload.sub == "42"
        assert payload.type == "access"

    def test_decode_invalid_token_returns_none(self):
        payload = decode_access_token("this.is.not.a.valid.jwt")

        assert payload is None

    def test_decode_token_with_wrong_secret_returns_none(self):
        fake_payload = {"sub": "42", "type": "access", "exp": time.time() + 900}
        fake_token = jwt.encode(fake_payload, "wrong-secret-key", algorithm=settings.jwt_algorithm)

        payload = decode_access_token(fake_token)

        assert payload is None

    def test_decode_expired_token_returns_none(self):
        expired_payload = {"sub": "42", "type": "access", "exp": time.time() - 10}
        expired_token = jwt.encode(expired_payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)

        payload = decode_access_token(expired_token)

        assert payload is None


class TestRefreshToken:
    def test_generate_refresh_token_is_url_safe_and_long(self):
        token = generate_refresh_token()

        assert len(token) > 50
        assert " " not in token

    def test_two_generated_tokens_are_different(self):
        token1 = generate_refresh_token()
        token2 = generate_refresh_token()

        assert token1 != token2

    def test_hash_token_is_deterministic(self):
        token = "some-random-refresh-token-value"

        assert hash_token(token) == hash_token(token)

    def test_different_tokens_produce_different_hashes(self):
        assert hash_token("token-a") != hash_token("token-b")


class TestEmailVerificationToken:
    def test_create_and_decode_verification_token(self):
        token = create_email_verification_token(user_id=7)
        user_id = decode_email_verification_token(token)

        assert user_id == 7

    def test_decode_invalid_verification_token_returns_none(self):
        user_id = decode_email_verification_token("garbage.token.value")

        assert user_id is None

    def test_access_token_cannot_be_used_as_verification_token(self):
        access_token = create_access_token(user_id=7)

        user_id = decode_email_verification_token(access_token)

        assert user_id is None