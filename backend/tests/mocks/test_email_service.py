import pytest
from unittest.mock import patch, AsyncMock

from app.services.email_service import send_verification_email
from app.services.auth_service import AuthService
from app.schemas.user import UserCreate


class TestEmailServiceDirectly:
    @patch("app.services.email_service.aiosmtplib.send", new_callable=AsyncMock)
    async def test_send_verification_email_calls_smtp(self, mock_smtp_send):
        await send_verification_email("user@example.com", "some-verification-token")

        mock_smtp_send.assert_called_once()

    @patch("app.services.email_service.aiosmtplib.send", new_callable=AsyncMock)
    async def test_verification_email_contains_correct_recipient(self, mock_smtp_send):
        await send_verification_email("recipient@example.com", "token123")

        sent_message = mock_smtp_send.call_args.args[0]
        assert sent_message["To"] == "recipient@example.com"

    @patch("app.services.email_service.aiosmtplib.send", new_callable=AsyncMock)
    async def test_verification_email_contains_token_in_link(self, mock_smtp_send):
        await send_verification_email("user@example.com", "unique-token-abc")

        sent_message = mock_smtp_send.call_args.args[0]
        html_part = sent_message.get_body(preferencelist=("html",))

        assert "unique-token-abc" in html_part.get_content()

    @patch("app.services.email_service.aiosmtplib.send", new_callable=AsyncMock)
    async def test_smtp_failure_raises_exception(self, mock_smtp_send):
     
        mock_smtp_send.side_effect = Exception("SMTP connection failed")

        with pytest.raises(Exception, match="SMTP connection failed"):
            await send_verification_email("user@example.com", "token")


class TestRegistrationTriggersEmail:
    

    @patch("app.services.auth_service.send_verification_email", new_callable=AsyncMock)
    async def test_register_triggers_verification_email(self, mock_send_email, db_session):
        auth_service = AuthService(db_session)

        user_data = UserCreate(email="newregister@example.com", password="SecurePass123")
        created_user = await auth_service.register_user(user_data)

        mock_send_email.assert_called_once()
        call_args = mock_send_email.call_args.args
        assert call_args[0] == "newregister@example.com"  # email
        assert created_user.is_email_verified is False

    @patch("app.services.auth_service.send_verification_email", new_callable=AsyncMock)
    async def test_resend_verification_does_not_send_if_already_verified(
        self, mock_send_email, db_session
    ):
        from app.models.user import User
        from app.core.security import hash_password

        user = User(
            email="alreadyverified@example.com",
            hashed_password=hash_password("Pass123"),
            is_email_verified=True,
        )
        db_session.add(user)
        await db_session.commit()

        auth_service = AuthService(db_session)
        await auth_service.resend_verification_email("alreadyverified@example.com")

        mock_send_email.assert_not_called()

    @patch("app.services.auth_service.send_verification_email", new_callable=AsyncMock)
    async def test_resend_verification_does_not_reveal_unknown_email(
        self, mock_send_email, db_session
    ):
        auth_service = AuthService(db_session)

        await auth_service.resend_verification_email("nonexistent@example.com")

        mock_send_email.assert_not_called()