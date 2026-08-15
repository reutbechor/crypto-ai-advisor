from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies.auth import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.dashboard import (
    DashboardResponse,
    DashboardUserResponse,
)
from app.schemas.onboarding import PreferenceResponse
from app.services.market import fetch_market_data
from app.services.news import select_personalized_news
from app.services.onboarding import get_user_preferences


router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("", response_model=DashboardResponse)
def read_dashboard(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> DashboardResponse:
    preferences = get_user_preferences(db, current_user.id)
    if preferences is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dashboard preferences were not found.",
        )

    market, market_status = fetch_market_data(preferences.crypto_assets)
    news, news_status = select_personalized_news(preferences.crypto_assets)

    return DashboardResponse(
        user=DashboardUserResponse(id=current_user.id, name=current_user.name),
        preferences=PreferenceResponse.model_validate(preferences),
        market=market,
        market_status=market_status,
        news=news,
        news_status=news_status,
    )
