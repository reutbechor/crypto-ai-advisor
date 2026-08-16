from sqlalchemy import func, select

from app.models import Preference, User


def create_authenticated_user(client, email="onboarding@example.com"):
    password = "Password123!"
    signup = client.post(
        "/api/auth/signup",
        json={"name": "Onboarding User", "email": email, "password": password},
    )
    login = client.post(
        "/api/auth/login",
        json={"email": email, "password": password},
    )
    return signup.json()["id"], {"Authorization": f"Bearer {login.json()['access_token']}"}


VALID_PREFERENCES = {
    "crypto_assets": ["bitcoin", "ethereum"],
    "investor_type": "hodler",
    "content_preferences": ["ai_insights", "market_news"],
}


def test_onboarding_is_atomic_repeat_safe_and_preferences_are_user_scoped(client, db_session):
    user_id, headers = create_authenticated_user(client)
    _, other_headers = create_authenticated_user(client, "other@example.com")

    completed = client.post("/api/onboarding", json=VALID_PREFERENCES, headers=headers)
    repeated = client.post("/api/onboarding", json=VALID_PREFERENCES, headers=headers)
    preferences = client.get("/api/onboarding/preferences", headers=headers)
    other_preferences = client.get("/api/onboarding/preferences", headers=other_headers)

    user = db_session.get(User, user_id)
    stored = db_session.scalar(select(Preference).where(Preference.user_id == user_id))
    assert completed.status_code == 200
    assert completed.json()["user"]["onboarding_completed"] is True
    assert user.onboarding_completed is True
    assert stored.crypto_assets == ["bitcoin", "ethereum"]
    assert stored.content_preferences == ["ai_insights", "market_news"]
    assert repeated.status_code == 409
    assert preferences.status_code == 200
    assert preferences.json() == VALID_PREFERENCES
    assert other_preferences.status_code == 404


def test_onboarding_rejects_invalid_or_client_owned_identity_without_partial_writes(
    client,
    db_session,
):
    user_id, headers = create_authenticated_user(client)
    invalid_payloads = [
        {**VALID_PREFERENCES, "crypto_assets": []},
        {**VALID_PREFERENCES, "crypto_assets": ["dogecoin"]},
        {**VALID_PREFERENCES, "investor_type": "swing_trader"},
        {**VALID_PREFERENCES, "content_preferences": ["signals"]},
        {**VALID_PREFERENCES, "crypto_assets": ["bitcoin", "bitcoin"]},
        {**VALID_PREFERENCES, "content_preferences": ["fun", "fun"]},
        {**VALID_PREFERENCES, "user_id": 999},
    ]

    for payload in invalid_payloads:
        response = client.post("/api/onboarding", json=payload, headers=headers)
        assert response.status_code == 422
        assert db_session.get(User, user_id).onboarding_completed is False
        assert db_session.scalar(select(func.count()).select_from(Preference)) == 0
