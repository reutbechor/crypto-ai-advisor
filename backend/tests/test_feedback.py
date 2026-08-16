import unittest
from types import SimpleNamespace

from fastapi.testclient import TestClient
from sqlalchemy import create_engine, func, insert, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.api.dependencies.auth import get_current_user
from app.db.session import get_db
from app.main import app
from app.models import Feedback, User
from app.services.feedback import get_feedback_state, toggle_feedback


def create_test_database():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    User.__table__.create(engine)
    Feedback.__table__.create(engine)
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


class FeedbackDatabaseTests(unittest.TestCase):
    def setUp(self):
        self.engine, self.session = create_test_database()

    def tearDown(self):
        self.session.close()
        self.engine.dispose()

    def test_vote_is_created_updated_and_toggled_off_without_duplicates(self):
        created = toggle_feedback(
            self.session,
            user_id=1,
            content_type="ai_insight",
            content_id="daily-2026-08-16",
            vote="up",
        )
        created_id = created.id

        updated = toggle_feedback(
            self.session,
            user_id=1,
            content_type="ai_insight",
            content_id="daily-2026-08-16",
            vote="down",
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
            self.session,
            user_id=1,
            content_type="ai_insight",
            content_id="daily-2026-08-16",
            vote="down",
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

        row = self.session.scalar(select(Feedback))
        self.assertEqual(created.status_code, 200)
        self.assertEqual(created.json()["vote"], "up")
        self.assertEqual(removed.status_code, 200)
        self.assertIsNone(removed.json()["vote"])
        self.assertIsNone(row)

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


if __name__ == "__main__":
    unittest.main()
