from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies.auth import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.auth import AuthUserResponse
from app.schemas.onboarding import (
    OnboardingRequest,
    OnboardingResponse,
    PreferenceResponse,
)
from app.services.onboarding import (
    OnboardingAlreadyCompletedError,
    OnboardingPersistenceError,
    complete_onboarding,
    get_user_preferences,
)


router = APIRouter(prefix="/onboarding", tags=["Onboarding"])


@router.post("", response_model=OnboardingResponse)
def save_onboarding(
    onboarding_data: OnboardingRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> OnboardingResponse:
    try:
        preference = complete_onboarding(db, current_user, onboarding_data)
    except OnboardingAlreadyCompletedError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Onboarding has already been completed.",
        ) from exc
    except OnboardingPersistenceError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to save onboarding preferences.",
        ) from exc

    return OnboardingResponse(
        message="Onboarding completed successfully.",
        user=AuthUserResponse.model_validate(current_user),
        preferences=PreferenceResponse.model_validate(preference),
    )


@router.get("/preferences", response_model=PreferenceResponse)
def read_preferences(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> PreferenceResponse:
    preference = get_user_preferences(db, current_user.id)
    if preference is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Onboarding preferences were not found.",
        )

    return PreferenceResponse.model_validate(preference)
