from collections.abc import Callable
from datetime import date, datetime, timezone
from typing import Literal

from pydantic import ValidationError
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.daily_content import DailyContent
from app.schemas.dashboard import AIInsightResponse, MarketCoinResponse, MemeResponse
from app.schemas.onboarding import CryptoAsset, InvestorType
from app.services.ai_insight import AIStatus, generate_ai_insight
from app.services.meme import MemeStatus, fetch_meme


DailyContentType = Literal["ai_insight", "meme"]
AIProducer = Callable[
    [InvestorType, list[CryptoAsset], list[MarketCoinResponse]],
    tuple[AIInsightResponse, AIStatus],
]
MemeProducer = Callable[[], tuple[MemeResponse | None, MemeStatus]]


def current_daily_date() -> date:
    return datetime.now(timezone.utc).date()


def _find_daily_content(
    db: Session,
    user_id: int,
    content_type: DailyContentType,
    content_date: date,
) -> DailyContent | None:
    return db.scalar(
        select(DailyContent).where(
            DailyContent.user_id == user_id,
            DailyContent.content_type == content_type,
            DailyContent.content_date == content_date,
        )
    )


def _persist_or_get(
    db: Session,
    user_id: int,
    content_type: DailyContentType,
    content_date: date,
    payload: dict,
) -> DailyContent:
    daily_content = DailyContent(
        user_id=user_id,
        content_type=content_type,
        content_date=content_date,
        payload=payload,
    )
    db.add(daily_content)

    try:
        db.commit()
        db.refresh(daily_content)
        return daily_content
    except IntegrityError:
        db.rollback()
        existing = _find_daily_content(
            db,
            user_id,
            content_type,
            content_date,
        )
        if existing is None:
            raise
        return existing


def get_or_create_daily_ai(
    db: Session,
    user_id: int,
    investor_type: InvestorType,
    selected_assets: list[CryptoAsset],
    market_data: list[MarketCoinResponse],
    *,
    for_date: date | None = None,
    producer: AIProducer = generate_ai_insight,
) -> tuple[AIInsightResponse, AIStatus, date]:
    content_date = for_date or current_daily_date()
    stored = _find_daily_content(db, user_id, "ai_insight", content_date)

    if stored is None:
        insight, status = producer(investor_type, selected_assets, market_data)
        insight = insight.model_copy(
            update={"id": f"ai-{content_date.isoformat()}"}
        )
        stored = _persist_or_get(
            db,
            user_id,
            "ai_insight",
            content_date,
            {
                **insight.model_dump(mode="json"),
                "ai_status": status,
            },
        )

    try:
        ai_status = stored.payload["ai_status"]
        if ai_status not in {"available", "fallback"}:
            raise ValueError("Stored daily AI status is invalid.")
        return (
            AIInsightResponse.model_validate(
                {
                    key: value
                    for key, value in stored.payload.items()
                    if key != "ai_status"
                }
            ),
            ai_status,
            content_date,
        )
    except (KeyError, TypeError, ValidationError) as exc:
        raise ValueError("Stored daily AI content is invalid.") from exc


def get_or_create_daily_meme(
    db: Session,
    user_id: int,
    *,
    for_date: date | None = None,
    producer: MemeProducer = fetch_meme,
) -> tuple[MemeResponse | None, MemeStatus, date]:
    content_date = for_date or current_daily_date()
    stored = _find_daily_content(db, user_id, "meme", content_date)

    if stored is None:
        meme, status = producer()
        payload = (
            {**meme.model_dump(mode="json"), "meme_status": status}
            if meme is not None
            else {"meme": None, "meme_status": status}
        )
        stored = _persist_or_get(
            db,
            user_id,
            "meme",
            content_date,
            payload,
        )

    try:
        meme_status = stored.payload["meme_status"]
        if meme_status not in {"available", "fallback", "unavailable"}:
            raise ValueError("Stored daily meme status is invalid.")
        meme_payload = (
            None
            if stored.payload.get("meme") is None and "meme" in stored.payload
            else {
                key: value
                for key, value in stored.payload.items()
                if key != "meme_status"
            }
        )
        return (
            MemeResponse.model_validate(meme_payload) if meme_payload is not None else None,
            meme_status,
            content_date,
        )
    except (KeyError, TypeError, ValidationError) as exc:
        raise ValueError("Stored daily meme content is invalid.") from exc
