import unittest
from datetime import UTC, date, datetime, timedelta
from types import SimpleNamespace
from unittest.mock import Mock

from fastapi.testclient import TestClient
from sqlalchemy import create_engine, func, insert, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.api.dependencies.auth import get_current_user
from app.db.session import get_db
from app.main import app
from app.models import DailyContent, Feedback, User
from app.schemas.dashboard import (
    AIInsightAudienceResponse,
    AIInsightResponse,
    MemeResponse,
)
from app.services.daily_content import get_or_create_daily_ai, get_or_create_daily_meme
from app.services.feedback import get_feedback_state, toggle_feedback


TEST_DATE = date(2026, 8, 16)


def create_test_database(include_daily_content=False):
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    tables = [User.__table__, Feedback.__table__]
    if include_daily_content:
        tables.append(DailyContent.__table__)
    for table in tables:
        table.create(engine)
    with engine.begin() as connection:
        connection.execute(
            insert(User.__table__),
            [
                {
                    "id": 1,
                    "name": "First User",
                    "email": "first@example.com",
                    "password_hash": "unused",
                    "onboarding_completed": True,
                },
                {
                    "id": 2,
                    "name": "Second User",
                    "email": "second@example.com",
                    "password_hash": "unused",
                    "onboarding_completed": True,
                },
            ],
        )
    return engine, Session(engine, expire_on_commit=False)


def make_insight(title):
    return AIInsightResponse(
        id="temporary",
        title=title,
        content=f"{title} content",
        generated_for=AIInsightAudienceResponse(
            investor_type="hodler",
            crypto_assets=["bitcoin"],
        ),
        generated_at=datetime(2026, 8, 16, 8, 30, tzinfo=UTC),
    )


def make_meme(identifier):
    return MemeResponse(
        id=identifier,
        title=f"Meme {identifier}",
        image_url=f"/memes/{identifier}.svg",
        source="CoinSight original",
        source_url=None,
        alt_text=f"Crypto meme {identifier}.",
    )


class FeedbackDatabaseTests(unittest.TestCase):
    def setUp(self):
        self.engine, self.session = create_test_database()

    def tearDown(self):
        self.session.close()
        self.engine.dispose()

    def test_vote_is_created_updated_and_toggled_off_without_duplicates(self):
        created = toggle_feedback(
            self.session, 1, "ai_insight", "ai-2026-08-16", "up"
        )
        created_id = created.id

        updated = toggle_feedback(
            self.session, 1, "ai_insight", "ai-2026-08-16", "down"
        )

        self.assertEqual(updated.id, created_id)
        self.assertEqual(updated.vote, "down")
        self.assertIsNotNone(updated.created_at)
        self.assertIsNotNone(updated.updated_at)
        self.assertEqual(
            self.session.scalar(select(func.count()).select_from(Feedback)),
            1,
        )

        removed = toggle_feedback(
            self.session, 1, "ai_insight", "ai-2026-08-16", "down"
        )

        self.assertIsNone(removed)
        self.assertEqual(
            self.session.scalar(select(func.count()).select_from(Feedback)),
            0,
        )

    def test_unique_constraint_blocks_duplicate_content_vote(self):
        self.session.add_all(
            [
                Feedback(user_id=1, content_type="news", content_id="btc-001", vote="up"),
                Feedback(user_id=1, content_type="news", content_id="btc-001", vote="down"),
            ]
        )

        with self.assertRaises(IntegrityError):
            self.session.commit()
        self.session.rollback()

    def test_feedback_state_is_isolated_by_user(self):
        toggle_feedback(self.session, 1, "news", "btc-001", "up")
        toggle_feedback(self.session, 1, "meme", "coinsight-refresh", "down")
        toggle_feedback(self.session, 2, "news", "btc-001", "down")

        first_user = get_feedback_state(self.session, 1)
        second_user = get_feedback_state(self.session, 2)

        self.assertEqual(first_user.news, {"btc-001": "up"})
        self.assertEqual(first_user.meme, {"coinsight-refresh": "down"})
        self.assertEqual(second_user.news, {"btc-001": "down"})
        self.assertEqual(second_user.meme, {})

    def test_model_declares_foreign_key_checks_and_timestamps(self):
        foreign_key = next(iter(Feedback.__table__.c.user_id.foreign_keys))
        constraint_names = {
            constraint.name for constraint in Feedback.__table__.constraints
        }

        self.assertEqual(foreign_key.target_fullname, "users.id")
        self.assertEqual(foreign_key.ondelete, "CASCADE")
        self.assertIn("uq_feedback_user_content", constraint_names)
        self.assertIn("ck_feedback_content_type", constraint_names)
        self.assertIn("ck_feedback_vote", constraint_names)
        self.assertIsNotNone(Feedback.__table__.c.created_at.server_default)
        self.assertIsNotNone(Feedback.__table__.c.updated_at.server_default)


class FeedbackApiTests(unittest.TestCase):
    def setUp(self):
        self.engine, self.session = create_test_database()
        self.client = TestClient(app)
        app.dependency_overrides[get_db] = lambda: self.session
        app.dependency_overrides[get_current_user] = lambda: SimpleNamespace(id=1)

    def tearDown(self):
        app.dependency_overrides.clear()
        self.session.close()
        self.engine.dispose()

    def test_put_feedback_uses_authenticated_user_and_toggles(self):
        payload = {
            "content_type": "news",
            "content_id": "btc-001",
            "vote": "up",
        }

        created = self.client.put("/api/feedback", json=payload)
        removed = self.client.put("/api/feedback", json=payload)

        self.assertEqual(created.status_code, 200)
        self.assertEqual(created.json()["vote"], "up")
        self.assertEqual(removed.status_code, 200)
        self.assertIsNone(removed.json()["vote"])
        self.assertIsNone(self.session.scalar(select(Feedback)))

        changed = self.client.put(
            "/api/feedback",
            json={**payload, "vote": "down"},
        )
        row = self.session.scalar(select(Feedback))
        self.assertEqual(changed.json()["vote"], "down")
        self.assertEqual(row.user_id, 1)

    def test_invalid_payloads_are_rejected(self):
        invalid_payloads = [
            {"content_type": "unknown", "content_id": "item", "vote": "up"},
            {"content_type": "news", "content_id": "item", "vote": "maybe"},
            {"content_type": "news", "content_id": "   ", "vote": "up"},
            {"content_type": "news", "content_id": "item", "vote": "up", "user_id": 2},
        ]

        for payload in invalid_payloads:
            with self.subTest(payload=payload):
                response = self.client.put("/api/feedback", json=payload)
                self.assertEqual(response.status_code, 422)

    def test_feedback_requires_authentication(self):
        app.dependency_overrides.pop(get_current_user)

        response = self.client.put(
            "/api/feedback",
            json={"content_type": "meme", "content_id": "meme-1", "vote": "up"},
        )

        self.assertEqual(response.status_code, 401)


class DailyFeedbackIdentityTests(unittest.TestCase):
    def setUp(self):
        self.engine, self.session = create_test_database(include_daily_content=True)

    def tearDown(self):
        self.session.close()
        self.engine.dispose()

    def test_ai_feedback_survives_same_day_and_next_day_starts_unvoted(self):
        next_date = TEST_DATE + timedelta(days=1)
        producer = Mock(
            side_effect=[
                (make_insight("Day one"), "available"),
                (make_insight("Day two"), "available"),
            ]
        )
        day_one, _, _ = get_or_create_daily_ai(
            self.session, 1, "hodler", ["bitcoin"], [],
            for_date=TEST_DATE, producer=producer,
        )
        toggle_feedback(self.session, 1, "ai_insight", day_one.id, "up")
        same_day, _, _ = get_or_create_daily_ai(
            self.session, 1, "hodler", ["bitcoin"], [],
            for_date=TEST_DATE, producer=producer,
        )
        day_two, _, _ = get_or_create_daily_ai(
            self.session, 1, "hodler", ["bitcoin"], [],
            for_date=next_date, producer=producer,
        )
        feedback = get_feedback_state(self.session, 1)

        self.assertEqual(day_one.id, same_day.id)
        self.assertEqual(day_one.id, "ai-2026-08-16")
        self.assertEqual(day_two.id, "ai-2026-08-17")
        self.assertEqual(feedback.ai_insight[day_one.id], "up")
        self.assertNotIn(day_two.id, feedback.ai_insight)
        self.assertEqual(producer.call_count, 2)

    def test_meme_feedback_survives_same_day_refresh(self):
        producer = Mock(
            side_effect=[
                (make_meme("daily-meme"), "available"),
                (make_meme("unexpected"), "available"),
            ]
        )
        first, _, _ = get_or_create_daily_meme(
            self.session, 1, for_date=TEST_DATE, producer=producer
        )
        toggle_feedback(self.session, 1, "meme", first.id, "down")
        refreshed, _, _ = get_or_create_daily_meme(
            self.session, 1, for_date=TEST_DATE, producer=producer
        )
        feedback = get_feedback_state(self.session, 1)

        self.assertEqual(first.id, refreshed.id)
        self.assertEqual(feedback.meme[first.id], "down")
        self.assertEqual(producer.call_count, 1)


if __name__ == "__main__":
    unittest.main()
