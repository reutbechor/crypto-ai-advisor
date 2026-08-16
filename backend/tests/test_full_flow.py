from datetime import UTC, date, datetime

from app.schemas.dashboard import (
    AIInsightAudienceResponse,
    AIInsightResponse,
    MemeResponse,
)


def test_signup_login_onboarding_dashboard_and_feedback_flow(client, monkeypatch):
    credentials = {
        "name": "Flow User",
        "email": "flow@example.com",
        "password": "Password123!",
    }
    signup = client.post("/api/auth/signup", json=credentials)
    login = client.post(
        "/api/auth/login",
        json={"email": credentials["email"], "password": credentials["password"]},
    )
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    before_onboarding = client.get("/api/dashboard", headers=headers)
    onboarding = client.post(
        "/api/onboarding",
        headers=headers,
        json={
            "crypto_assets": ["bitcoin"],
            "investor_type": "hodler",
            "content_preferences": ["ai_insights", "fun"],
        },
    )
    returning_login = client.post(
        "/api/auth/login",
        json={"email": credentials["email"], "password": credentials["password"]},
    )

    daily_date = date(2026, 8, 16)
    insight = AIInsightResponse(
        id="ai-2026-08-16",
        title="Daily context",
        content="A deterministic mocked insight for the full API flow.",
        generated_for=AIInsightAudienceResponse(
            investor_type="hodler",
            crypto_assets=["bitcoin"],
        ),
        generated_at=datetime(2026, 8, 16, 8, 0, tzinfo=UTC),
    )
    meme = MemeResponse(
        id="daily-meme-2026-08-16",
        title="Daily meme",
        image_url="/memes/daily.svg",
        source="CoinSight original",
        alt_text="A deterministic mocked daily meme.",
    )
    monkeypatch.setattr("app.api.routes.dashboard.fetch_market_data", lambda _assets: ([], "unavailable"))
    monkeypatch.setattr("app.api.routes.dashboard.select_personalized_news", lambda _assets: ([], "fallback"))
    monkeypatch.setattr("app.api.routes.dashboard.current_daily_date", lambda: daily_date)
    monkeypatch.setattr(
        "app.api.routes.dashboard.get_or_create_daily_ai",
        lambda *_args, **_kwargs: (insight, "fallback", daily_date),
    )
    monkeypatch.setattr(
        "app.api.routes.dashboard.get_or_create_daily_meme",
        lambda *_args, **_kwargs: (meme, "fallback", daily_date),
    )

    first_dashboard = client.get("/api/dashboard", headers=headers)
    vote = client.put(
        "/api/feedback",
        headers=headers,
        json={"content_type": "ai_insight", "content_id": insight.id, "vote": "up"},
    )
    refreshed_dashboard = client.get("/api/dashboard", headers=headers)
    serialized_dashboard = refreshed_dashboard.text.casefold()

    assert signup.status_code == 201
    assert login.status_code == 200
    assert login.json()["user"]["onboarding_completed"] is False
    assert before_onboarding.status_code == 404
    assert onboarding.status_code == 200
    assert returning_login.status_code == 200
    assert returning_login.json()["user"]["onboarding_completed"] is True
    assert first_dashboard.status_code == 200
    assert first_dashboard.json()["ai_insight"]["id"] == insight.id
    assert first_dashboard.json()["meme"]["id"] == meme.id
    assert vote.status_code == 200
    assert refreshed_dashboard.json()["feedback"]["ai_insight"] == {insight.id: "up"}
    for secret_field in ("password_hash", "access_token", "jwt_secret", credentials["email"]):
        assert secret_field.casefold() not in serialized_dashboard

