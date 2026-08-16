import unittest
from datetime import UTC, datetime
from types import SimpleNamespace
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.api.dependencies.auth import get_current_user
from app.db.session import get_db
from app.main import app
from app.models.user import User
from app.schemas.dashboard import (
    AIInsightAudienceResponse,
    AIInsightResponse,
    MemeResponse,
)


class DashboardMemeApiTests(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def tearDown(self):
        app.dependency_overrides.clear()

    def test_unauthenticated_dashboard_is_unauthorized(self):
        response = self.client.get("/api/dashboard")

        self.assertEqual(response.status_code, 401)

    @patch("app.api.routes.dashboard.fetch_meme")
    @patch("app.api.routes.dashboard.generate_ai_insight")
    @patch("app.api.routes.dashboard.select_personalized_news")
    @patch("app.api.routes.dashboard.fetch_market_data")
    @patch("app.api.routes.dashboard.get_user_preferences")
    def test_authenticated_dashboard_includes_normalized_meme(
        self,
        get_preferences,
        fetch_market,
        select_news,
        generate_insight,
        fetch_dashboard_meme,
    ):
        user = User(id=7, name="Demo User", email="demo@example.com", password_hash="unused")
        preferences = SimpleNamespace(
            crypto_assets=["bitcoin"],
            investor_type="hodler",
            content_preferences=["fun"],
        )
        insight = AIInsightResponse(
            title="Market context",
            content="Keep short-term movement in context.",
            generated_for=AIInsightAudienceResponse(
                investor_type="hodler",
                crypto_assets=["bitcoin"],
            ),
            generated_at=datetime.now(UTC),
        )
        meme = MemeResponse(
            id="coinsight-refresh",
            title="Chart refresh mood",
            image_url="/memes/chart-refresh.svg",
            source="CoinSight original",
            source_url=None,
            alt_text="Illustrated crypto chart refresh meme.",
        )

        app.dependency_overrides[get_current_user] = lambda: user
        app.dependency_overrides[get_db] = lambda: None
        get_preferences.return_value = preferences
        fetch_market.return_value = ([], "unavailable")
        select_news.return_value = ([], "fallback")
        generate_insight.return_value = (insight, "fallback")
        fetch_dashboard_meme.return_value = (meme, "fallback")

        response = self.client.get("/api/dashboard")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["meme"]["id"], "coinsight-refresh")
        self.assertEqual(response.json()["meme_status"], "fallback")


if __name__ == "__main__":
    unittest.main()
