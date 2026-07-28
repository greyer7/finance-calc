import pytest
from httpx import AsyncClient

from app.core.security import create_access_token, hash_password
from app.models.user import User


async def _create_verified_user_and_token(db_session, email: str) -> str:
    user = User(
        email=email,
        hashed_password=hash_password("SomePass123"),
        is_email_verified=True,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    return create_access_token(user.id)


class TestLoanAnnuityEndpoint:
    async def test_calculate_loan_annuity_success(self, client: AsyncClient, db_session):
        token = await _create_verified_user_and_token(db_session, "loan1@example.com")

        response = await client.post(
            "/api/v1/calculate/loan/annuity",
            json={"principal": 100000, "annual_rate": 12, "term_months": 12, "currency": "USD"},
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["monthly_payment"] == pytest.approx(8884.88, abs=0.01)
        assert len(data["schedule"]) == 12

    async def test_calculate_loan_annuity_without_auth_fails(self, client: AsyncClient):
        response = await client.post(
            "/api/v1/calculate/loan/annuity",
            json={"principal": 100000, "annual_rate": 12, "term_months": 12, "currency": "USD"},
        )

        assert response.status_code == 401

    async def test_calculate_loan_annuity_with_negative_principal_fails(
        self, client: AsyncClient, db_session
    ):
        token = await _create_verified_user_and_token(db_session, "loan2@example.com")

        response = await client.post(
            "/api/v1/calculate/loan/annuity",
            json={"principal": -1000, "annual_rate": 12, "term_months": 12, "currency": "USD"},
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 422  

    async def test_unverified_user_cannot_calculate(self, client: AsyncClient, db_session):
        user = User(
            email="unverified_calc@example.com",
            hashed_password=hash_password("SomePass123"),
            is_email_verified=False,  
        )
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)
        token = create_access_token(user.id)

        response = await client.post(
            "/api/v1/calculate/loan/annuity",
            json={"principal": 100000, "annual_rate": 12, "term_months": 12, "currency": "USD"},
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 403


class TestDepositEndpoint:
    async def test_calculate_deposit_success(self, client: AsyncClient, db_session):
        token = await _create_verified_user_and_token(db_session, "deposit1@example.com")

        response = await client.post(
            "/api/v1/calculate/deposit",
            json={
                "principal": 100000,
                "annual_rate": 12,
                "term_months": 12,
                "compounding_frequency": "monthly",
                "currency": "USD",
            },
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["final_amount"] == pytest.approx(112682.50, abs=0.5)

    async def test_calculate_deposit_invalid_frequency_fails(self, client: AsyncClient, db_session):
        token = await _create_verified_user_and_token(db_session, "deposit2@example.com")

        response = await client.post(
            "/api/v1/calculate/deposit",
            json={
                "principal": 100000,
                "annual_rate": 12,
                "term_months": 12,
                "compounding_frequency": "weekly", 
                "currency": "USD",
            },
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 422


class TestInflationEndpoint:
    async def test_calculate_inflation_success(self, client: AsyncClient, db_session):
        token = await _create_verified_user_and_token(db_session, "inflation1@example.com")

        response = await client.post(
            "/api/v1/calculate/inflation",
            json={"amount": 10000, "annual_inflation_rate": 8, "term_years": 5, "currency": "USD"},
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["adjusted_value"] == pytest.approx(6805.83, abs=0.5)


class TestCalculationHistory:
    async def test_history_returns_saved_calculations(self, client: AsyncClient, db_session):
        token = await _create_verified_user_and_token(db_session, "history1@example.com")
        headers = {"Authorization": f"Bearer {token}"}

        await client.post(
            "/api/v1/calculate/loan/annuity",
            json={"principal": 100000, "annual_rate": 12, "term_months": 12, "currency": "USD"},
            headers=headers,
        )
        await client.post(
            "/api/v1/calculate/inflation",
            json={"amount": 10000, "annual_inflation_rate": 8, "term_years": 5, "currency": "USD"},
            headers=headers,
        )

        response = await client.get("/api/v1/calculate/history", headers=headers)

        assert response.status_code == 200
        history = response.json()
        assert len(history) == 2

    async def test_history_filters_by_type(self, client: AsyncClient, db_session):
        token = await _create_verified_user_and_token(db_session, "history2@example.com")
        headers = {"Authorization": f"Bearer {token}"}

        await client.post(
            "/api/v1/calculate/loan/annuity",
            json={"principal": 100000, "annual_rate": 12, "term_months": 12, "currency": "USD"},
            headers=headers,
        )
        await client.post(
            "/api/v1/calculate/inflation",
            json={"amount": 10000, "annual_inflation_rate": 8, "term_years": 5, "currency": "USD"},
            headers=headers,
        )

        response = await client.get(
            "/api/v1/calculate/history?calculation_type=loan_annuity", headers=headers
        )

        history = response.json()
        assert len(history) == 1
        assert history[0]["calculation_type"] == "loan_annuity"

    async def test_delete_calculation_removes_it(self, client: AsyncClient, db_session):
        token = await _create_verified_user_and_token(db_session, "history3@example.com")
        headers = {"Authorization": f"Bearer {token}"}

        calc_response = await client.post(
            "/api/v1/calculate/loan/annuity",
            json={"principal": 100000, "annual_rate": 12, "term_months": 12, "currency": "USD"},
            headers=headers,
        )
        history_response = await client.get("/api/v1/calculate/history", headers=headers)
        calculation_id = history_response.json()[0]["id"]

        delete_response = await client.delete(
            f"/api/v1/calculate/history/{calculation_id}", headers=headers
        )
        assert delete_response.status_code == 404

        history_after = await client.get("/api/v1/calculate/history", headers=headers)
        assert len(history_after.json()) == 0

    async def test_cannot_delete_other_users_calculation(self, client: AsyncClient, db_session):
        token1 = await _create_verified_user_and_token(db_session, "owner@example.com")
        token2 = await _create_verified_user_and_token(db_session, "intruder@example.com")

        calc_response = await client.post(
            "/api/v1/calculate/loan/annuity",
            json={"principal": 100000, "annual_rate": 12, "term_months": 12, "currency": "USD"},
            headers={"Authorization": f"Bearer {token1}"},
        )

        history_response = await client.get(
            "/api/v1/calculate/history", headers={"Authorization": f"Bearer {token1}"}
        )
        calculation_id = history_response.json()[0]["id"]

        delete_response = await client.delete(
            f"/api/v1/calculate/history/{calculation_id}",
            headers={"Authorization": f"Bearer {token2}"},
        )

        assert delete_response.status_code == 204

        owner_history = await client.get(
            "/api/v1/calculate/history", headers={"Authorization": f"Bearer {token1}"}
        )
        assert len(owner_history.json()) == 1