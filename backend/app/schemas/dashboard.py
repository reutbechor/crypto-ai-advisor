from datetime import datetime
from typing import Literal

from pydantic import BaseModel

from app.schemas.onboarding import PreferenceResponse


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
    source: str
    published_at: datetime
    related_assets: list[str]
    url: str | None = None


class DashboardResponse(BaseModel):
    user: DashboardUserResponse
    preferences: PreferenceResponse
    market: list[MarketCoinResponse]
    market_status: Literal["available", "unavailable"]
    news: list[NewsItemResponse]
    news_status: Literal["fallback", "unavailable"]
