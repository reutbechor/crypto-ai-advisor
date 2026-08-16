from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, Field

from app.schemas.feedback import DashboardFeedbackResponse
from app.schemas.onboarding import CryptoAsset, InvestorType, PreferenceResponse


class DashboardUserResponse(BaseModel):
    id: int
    name: str


class MarketCoinResponse(BaseModel):
    id: str
    name: str
    symbol: str
    current_price: float
    price_change_percentage_24h: float
    market_cap: float | None = None
    last_updated: datetime | None = None


class NewsItemResponse(BaseModel):
    id: str
    title: str
    summary: str
    content: str
    source: str
    published_at: datetime
    related_assets: list[str]
    url: str | None = None


class AIInsightAudienceResponse(BaseModel):
    investor_type: InvestorType
    crypto_assets: list[CryptoAsset]


class AIInsightResponse(BaseModel):
    id: str
    title: str
    content: str
    generated_for: AIInsightAudienceResponse
    generated_at: datetime


class MemeResponse(BaseModel):
    id: str = Field(min_length=1, max_length=120)
    title: str = Field(min_length=1, max_length=180)
    image_url: str = Field(min_length=1, max_length=2048)
    source: str = Field(min_length=1, max_length=120)
    source_url: str | None = Field(default=None, max_length=2048)
    alt_text: str = Field(min_length=1, max_length=240)


class DashboardResponse(BaseModel):
    daily_date: date
    user: DashboardUserResponse
    preferences: PreferenceResponse
    market: list[MarketCoinResponse]
    market_status: Literal["available", "unavailable"]
    news: list[NewsItemResponse]
    news_status: Literal["fallback", "unavailable"]
    ai_insight: AIInsightResponse
    ai_status: Literal["available", "fallback"]
    meme: MemeResponse | None
    meme_status: Literal["available", "fallback", "unavailable"]
    feedback: DashboardFeedbackResponse
