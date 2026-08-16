import unittest
from datetime import UTC, date, datetime
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
from app.schemas.feedback import DashboardFeedbackResponse


class DashboardMemeApiTests(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def tearDown(self):
        app.dependency_overrides.clear()

    def test_unauthenticated_dashboard_is_unauthorized(self):
        response = self.client.get("/api/dashboard")

        self.assertEqual(response.status_code, 401)

    @patch("app.api.routes.dashboard.get_feedback_state")
    @patch("app.api.routes.dashboard.get_or_create_daily_meme")
    @patch("app.api.routes.dashboard.get_or_create_daily_ai")
    @patch("app.api.routes.dashboard.current_daily_date")
    @patch("app.api.routes.dashboard.select_personalized_news")
    @patch("app.api.routes.dashboard.fetch_market_data")
    @patch("app.api.routes.dashboard.get_user_preferences")
    def test_authenticated_dashboard_includes_normalized_meme(
        self,
        get_preferences,
        fetch_market,
        select_news,
        get_daily_date,
        get_daily_insight,
        get_daily_meme,
        get_feedback,
    ):
        user = User(id=7, name="Demo User", email="demo@example.com", password_hash="unused")
        preferences = SimpleNamespace(
            crypto_assets=["bitcoin"],
            investor_type="hodler",
            content_preferences=["fun"],
        )
        insight = AIInsightResponse(
            id="ai-2026-08-16",
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
        daily_date = date(2026, 8, 16)
        get_daily_date.return_value = daily_date
        get_daily_insight.return_value = (insight, "fallback", daily_date)
        get_daily_meme.return_value = (meme, "fallback", daily_date)
        get_feedback.return_value = DashboardFeedbackResponse(
            news={"story-1": "up"},
            ai_insight={"ai-2026-08-16": "down"},
            meme={"coinsight-refresh": "up"},
        )

        response = self.client.get("/api/dashboard")
        serialized_response = response.text

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["daily_date"], "2026-08-16")
        self.assertEqual(response.json()["meme"]["id"], "coinsight-refresh")
        self.assertEqual(response.json()["meme_status"], "fallback")
        self.assertNotIn("test-demo-key-not-a-real-secret", serialized_response)
        self.assertEqual(
            response.json()["feedback"]["ai_insight"],
            {"ai-2026-08-16": "down"},
        )
        self.assertEqual(
            response.json()["feedback"]["meme"],
            {"coinsight-refresh": "up"},
        )
        get_daily_insight.assert_called_once_with(
            None,
            7,
            "hodler",
            ["bitcoin"],
            [],
            for_date=daily_date,
        )
        get_daily_meme.assert_called_once_with(
            None,
            7,
            for_date=daily_date,
        )
        get_feedback.assert_called_once_with(None, 7)


if __name__ == "__main__":
    unittest.main()
