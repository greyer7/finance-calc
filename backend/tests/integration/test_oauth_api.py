import respx
import httpx
from httpx import AsyncClient

from app.config import settings
from app.utils.redis_client import redis_client


async def _get_state_from_login_redirect(client: AsyncClient, provider: str) -> str:
    """Хелпер: викликає /oauth/{provider}/login, витягує state з Location-заголовка редіректу."""
    response = await client.get(f"/api/v1/oauth/{provider}/login", follow_redirects=False)
    assert response.status_code in (302, 307)

    location = response.headers["location"]
    state = location.split("state=")[1].split("&")[0]
    return state


class TestGoogleOAuth:
    async def test_google_login_redirects_with_state(self, client: AsyncClient):
        response = await client.get("/api/v1/oauth/google/login", follow_redirects=False)

        assert response.status_code in (302, 307)
        assert "accounts.google.com" in response.headers["location"]
        assert "state=" in response.headers["location"]

    @respx.mock
    async def test_google_callback_creates_new_user(self, client: AsyncClient):
        state = await _get_state_from_login_redirect(client, "google")

        respx.post("https://oauth2.googleapis.com/token").mock(
            return_value=httpx.Response(200, json={"access_token": "fake-google-token"})
        )
        respx.get("https://www.googleapis.com/oauth2/v3/userinfo").mock(
            return_value=httpx.Response(200, json={
                "sub": "1234567890",
                "email": "googleuser@example.com",
                "email_verified": True,
            })
        )

        response = await client.get(
            f"/api/v1/oauth/google/callback?code=fake-code&state={state}",
            follow_redirects=False,
        )

        assert response.status_code in (302, 307)
        redirect_location = response.headers["location"]
        assert f"{settings.frontend_url}/oauth-success" in redirect_location
        assert "access_token=" in redirect_location
        assert "refresh_token=" in redirect_location

    @respx.mock
    async def test_google_callback_reuses_existing_user(self, client: AsyncClient, db_session):
        from app.models.user import User

        existing_user = User(
            email="existing@example.com",
            oauth_provider="google",
            oauth_id="9999999999",
            is_email_verified=True,
        )
        db_session.add(existing_user)
        await db_session.commit()

        state = await _get_state_from_login_redirect(client, "google")

        respx.post("https://oauth2.googleapis.com/token").mock(
            return_value=httpx.Response(200, json={"access_token": "fake-token"})
        )
        respx.get("https://www.googleapis.com/oauth2/v3/userinfo").mock(
            return_value=httpx.Response(200, json={
                "sub": "9999999999",
                "email": "existing@example.com",
                "email_verified": True,
            })
        )

        response = await client.get(
            f"/api/v1/oauth/google/callback?code=fake-code&state={state}",
            follow_redirects=False,
        )

        assert response.status_code in (302, 307)
        from sqlalchemy import select
        result = await db_session.execute(select(User).where(User.email == "existing@example.com"))
        users = result.scalars().all()
        assert len(users) == 1

    async def test_callback_with_invalid_state_fails(self, client: AsyncClient):
        response = await client.get(
            "/api/v1/oauth/google/callback?code=fake-code&state=totally-made-up-state",
            follow_redirects=False,
        )

        assert response.status_code == 400

    async def test_callback_state_cannot_be_reused(self, client: AsyncClient):
        state = await _get_state_from_login_redirect(client, "google")

        with respx.mock:
            respx.post("https://oauth2.googleapis.com/token").mock(
                return_value=httpx.Response(200, json={"access_token": "fake-token"})
            )
            respx.get("https://www.googleapis.com/oauth2/v3/userinfo").mock(
                return_value=httpx.Response(200, json={
                    "sub": "111",
                    "email": "onetime@example.com",
                    "email_verified": True,
                })
            )

            first_attempt = await client.get(
                f"/api/v1/oauth/google/callback?code=fake-code&state={state}",
                follow_redirects=False,
            )
            assert first_attempt.status_code in (302, 307)

        second_attempt = await client.get(
            f"/api/v1/oauth/google/callback?code=fake-code&state={state}",
            follow_redirects=False,
        )
        assert second_attempt.status_code == 400

    async def test_state_from_github_cannot_be_used_for_google_callback(self, client: AsyncClient):
        github_state = await _get_state_from_login_redirect(client, "github")

        response = await client.get(
            f"/api/v1/oauth/google/callback?code=fake-code&state={github_state}",
            follow_redirects=False,
        )

        assert response.status_code == 400


class TestGitHubOAuth:
    @respx.mock
    async def test_github_callback_creates_new_user(self, client: AsyncClient):
        state = await _get_state_from_login_redirect(client, "github")

        respx.post("https://github.com/login/oauth/access_token").mock(
            return_value=httpx.Response(200, json={"access_token": "fake-github-token"})
        )
        respx.get("https://api.github.com/user").mock(
            return_value=httpx.Response(200, json={
                "id": 555555,
                "email": "githubuser@example.com",
            })
        )

        response = await client.get(
            f"/api/v1/oauth/github/callback?code=fake-code&state={state}",
            follow_redirects=False,
        )

        assert response.status_code in (302, 307)
        assert "access_token=" in response.headers["location"]

    @respx.mock
    async def test_github_callback_fetches_email_when_hidden(self, client: AsyncClient):
        state = await _get_state_from_login_redirect(client, "github")

        respx.post("https://github.com/login/oauth/access_token").mock(
            return_value=httpx.Response(200, json={"access_token": "fake-github-token"})
        )
        respx.get("https://api.github.com/user").mock(
            return_value=httpx.Response(200, json={"id": 777777, "email": None})
        )
        respx.get("https://api.github.com/user/emails").mock(
            return_value=httpx.Response(200, json=[
                {"email": "secondary@example.com", "primary": False, "verified": True},
                {"email": "primary-hidden@example.com", "primary": True, "verified": True},
            ])
        )

        response = await client.get(
            f"/api/v1/oauth/github/callback?code=fake-code&state={state}",
            follow_redirects=False,
        )

        assert response.status_code in (302, 307)

    @respx.mock
    async def test_github_token_exchange_failure_returns_401(self, client: AsyncClient):
        state = await _get_state_from_login_redirect(client, "github")

        respx.post("https://github.com/login/oauth/access_token").mock(
            return_value=httpx.Response(200, json={"error": "bad_verification_code"})
        )

        response = await client.get(
            f"/api/v1/oauth/github/callback?code=invalid-code&state={state}",
            follow_redirects=False,
        )

        assert response.status_code == 401