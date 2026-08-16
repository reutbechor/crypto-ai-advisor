import unittest
from datetime import UTC, date, datetime, timedelta
from unittest.mock import Mock

from sqlalchemy import create_engine, func, select
from sqlalchemy.dialects import postgresql
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool
from sqlalchemy.schema import CreateTable

from app.db.base import Base
from app.models import DailyContent, User
from app.schemas.dashboard import (
    AIInsightAudienceResponse,
    AIInsightResponse,
    MemeResponse,
)
from app.services.daily_content import (
    _persist_or_get,
    get_or_create_daily_ai,
    get_or_create_daily_meme,
)


TEST_DATE = date(2026, 8, 16)


def make_insight(title: str) -> AIInsightResponse:
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


def make_meme(identifier: str) -> MemeResponse:
    return MemeResponse(
        id=identifier,
        title=f"Meme {identifier}",
        image_url=f"/memes/{identifier}.svg",
        source="CoinSight original",
        source_url=None,
        alt_text=f"Crypto meme {identifier}.",
    )


class DailyContentTests(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine(
            "sqlite://",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        self.tables = [User.__table__, DailyContent.__table__]
        Base.metadata.create_all(self.engine, tables=self.tables)
        with Session(self.engine) as db:
            db.add_all(
                [
                    User(
                        id=1,
                        name="First User",
                        email="first@example.com",
                        password_hash="unused",
                    ),
                    User(
                        id=2,
                        name="Second User",
                        email="second@example.com",
                        password_hash="unused",
                    ),
                ]
            )
            db.commit()

    def tearDown(self):
        Base.metadata.drop_all(self.engine, tables=reversed(self.tables))
        self.engine.dispose()

    def test_same_day_ai_is_generated_once_and_reused(self):
        producer = Mock(
            side_effect=[
                (make_insight("First insight"), "available"),
                (make_insight("Unexpected insight"), "available"),
            ]
        )

        with Session(self.engine) as db:
            first, first_status, _ = get_or_create_daily_ai(
                db,
                1,
                "hodler",
                ["bitcoin"],
                [],
                for_date=TEST_DATE,
                producer=producer,
            )
            second, second_status, _ = get_or_create_daily_ai(
                db,
                1,
                "hodler",
                ["bitcoin"],
                [],
                for_date=TEST_DATE,
                producer=producer,
            )

            self.assertEqual(first, second)
            self.assertEqual(first.id, "ai-2026-08-16")
            self.assertEqual(first_status, second_status)
            self.assertEqual(producer.call_count, 1)
            self.assertEqual(
                db.scalar(select(func.count()).select_from(DailyContent)),
                1,
            )

    def test_next_day_creates_new_ai_content(self):
        next_date = TEST_DATE + timedelta(days=1)
        producer = Mock(
            side_effect=[
                (make_insight("Day one"), "available"),
                (make_insight("Day two"), "available"),
            ]
        )

        with Session(self.engine) as db:
            first, _, _ = get_or_create_daily_ai(
                db, 1, "hodler", ["bitcoin"], [],
                for_date=TEST_DATE, producer=producer,
            )
            second, _, _ = get_or_create_daily_ai(
                db, 1, "hodler", ["bitcoin"], [],
                for_date=next_date, producer=producer,
            )

            self.assertNotEqual(first.title, second.title)
            self.assertEqual(second.id, "ai-2026-08-17")
            self.assertEqual(producer.call_count, 2)
            stored_dates = db.scalars(
                select(DailyContent.content_date)
                .where(
                    DailyContent.user_id == 1,
                    DailyContent.content_type == "ai_insight",
                )
                .order_by(DailyContent.content_date)
            ).all()
            self.assertEqual(stored_dates, [TEST_DATE, next_date])

    def test_same_day_meme_is_selected_once_and_reused(self):
        producer = Mock(
            side_effect=[
                (make_meme("first"), "available"),
                (make_meme("unexpected"), "available"),
            ]
        )

        with Session(self.engine) as db:
            first, first_status, _ = get_or_create_daily_meme(
                db, 1, for_date=TEST_DATE, producer=producer
            )
            second, second_status, _ = get_or_create_daily_meme(
                db, 1, for_date=TEST_DATE, producer=producer
            )

            self.assertEqual(first, second)
            self.assertEqual(first_status, second_status)
            self.assertEqual(producer.call_count, 1)

    def test_next_day_creates_new_meme_content(self):
        next_date = TEST_DATE + timedelta(days=1)
        producer = Mock(
            side_effect=[
                (make_meme("day-one"), "available"),
                (make_meme("day-two"), "available"),
            ]
        )

        with Session(self.engine) as db:
            first, _, _ = get_or_create_daily_meme(
                db, 1, for_date=TEST_DATE, producer=producer
            )
            second, _, _ = get_or_create_daily_meme(
                db, 1, for_date=next_date, producer=producer
            )

            self.assertNotEqual(first.id, second.id)
            self.assertEqual(producer.call_count, 2)
            stored_dates = db.scalars(
                select(DailyContent.content_date)
                .where(
                    DailyContent.user_id == 1,
                    DailyContent.content_type == "meme",
                )
                .order_by(DailyContent.content_date)
            ).all()
            self.assertEqual(stored_dates, [TEST_DATE, next_date])

    def test_daily_content_is_isolated_between_users(self):
        ai_producer = Mock(
            side_effect=[
                (make_insight("First user"), "available"),
                (make_insight("Second user"), "available"),
            ]
        )
        meme_producer = Mock(
            side_effect=[
                (make_meme("first-user"), "available"),
                (make_meme("second-user"), "available"),
            ]
        )

        with Session(self.engine) as db:
            first_user, _, _ = get_or_create_daily_ai(
                db, 1, "hodler", ["bitcoin"], [],
                for_date=TEST_DATE, producer=ai_producer,
            )
            second_user, _, _ = get_or_create_daily_ai(
                db, 2, "hodler", ["bitcoin"], [],
                for_date=TEST_DATE, producer=ai_producer,
            )
            first_user_again, _, _ = get_or_create_daily_ai(
                db, 1, "hodler", ["bitcoin"], [],
                for_date=TEST_DATE, producer=ai_producer,
            )
            first_meme, _, _ = get_or_create_daily_meme(
                db, 1, for_date=TEST_DATE, producer=meme_producer
            )
            second_meme, _, _ = get_or_create_daily_meme(
                db, 2, for_date=TEST_DATE, producer=meme_producer
            )
            first_meme_again, _, _ = get_or_create_daily_meme(
                db, 1, for_date=TEST_DATE, producer=meme_producer
            )

            self.assertEqual(first_user.title, "First user")
            self.assertEqual(second_user.title, "Second user")
            self.assertEqual(first_user_again, first_user)
            self.assertEqual(ai_producer.call_count, 2)
            self.assertEqual(first_meme.id, "first-user")
            self.assertEqual(second_meme.id, "second-user")
            self.assertEqual(first_meme_again, first_meme)
            self.assertEqual(meme_producer.call_count, 2)

    def test_fallback_ai_and_meme_are_persisted_for_the_day(self):
        ai_producer = Mock(return_value=(make_insight("Fallback"), "fallback"))
        meme_producer = Mock(return_value=(make_meme("fallback"), "fallback"))

        with Session(self.engine) as db:
            first_ai, ai_status, _ = get_or_create_daily_ai(
                db, 1, "hodler", ["bitcoin"], [],
                for_date=TEST_DATE, producer=ai_producer,
            )
            second_ai, _, _ = get_or_create_daily_ai(
                db, 1, "hodler", ["bitcoin"], [],
                for_date=TEST_DATE, producer=ai_producer,
            )
            first_meme, meme_status, _ = get_or_create_daily_meme(
                db, 1, for_date=TEST_DATE, producer=meme_producer
            )
            second_meme, _, _ = get_or_create_daily_meme(
                db, 1, for_date=TEST_DATE, producer=meme_producer
            )

            self.assertEqual(ai_status, "fallback")
            self.assertEqual(meme_status, "fallback")
            self.assertEqual(first_ai, second_ai)
            self.assertEqual(first_meme, second_meme)
            self.assertEqual(ai_producer.call_count, 1)
            self.assertEqual(meme_producer.call_count, 1)

    def test_unique_constraint_rejects_duplicate_daily_content(self):
        with Session(self.engine) as db:
            db.add_all(
                [
                    DailyContent(
                        user_id=1,
                        content_type="meme",
                        content_date=TEST_DATE,
                        payload={"meme": None, "meme_status": "unavailable"},
                    ),
                    DailyContent(
                        user_id=1,
                        content_type="meme",
                        content_date=TEST_DATE,
                        payload={"meme": None, "meme_status": "unavailable"},
                    ),
                ]
            )

            with self.assertRaises(IntegrityError):
                db.commit()

    def test_race_conflict_rolls_back_and_returns_winner(self):
        winner_payload = {"meme": None, "meme_status": "unavailable"}
        with Session(self.engine) as winner_db:
            winner = DailyContent(
                user_id=1,
                content_type="meme",
                content_date=TEST_DATE,
                payload=winner_payload,
            )
            winner_db.add(winner)
            winner_db.commit()
            winner_id = winner.id

        with Session(self.engine) as losing_db:
            result = _persist_or_get(
                losing_db,
                1,
                "meme",
                TEST_DATE,
                {"meme": make_meme("loser").model_dump(mode="json")},
            )

            self.assertEqual(result.id, winner_id)
            self.assertEqual(result.payload, winner_payload)
            self.assertTrue(losing_db.is_active)

    def test_postgresql_ddl_uses_jsonb_and_named_unique_constraint(self):
        ddl = str(
            CreateTable(DailyContent.__table__).compile(
                dialect=postgresql.dialect()
            )
        )

        self.assertIn("JSONB", ddl)
        self.assertIn("uq_daily_content_user_type_date", ddl)
        self.assertIn("ck_daily_content_type", ddl)


if __name__ == "__main__":
    unittest.main()
