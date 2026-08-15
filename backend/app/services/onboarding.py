from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from app.models.preference import Preference
from app.models.user import User
from app.schemas.onboarding import OnboardingRequest


class OnboardingAlreadyCompletedError(Exception):
    pass


class OnboardingPersistenceError(Exception):
    pass


def complete_onboarding(
    db: Session,
    user: User,
    onboarding_data: OnboardingRequest,
) -> Preference:
    if user.onboarding_completed:
        raise OnboardingAlreadyCompletedError

    existing_preference_id = db.scalar(
        select(Preference.id).where(Preference.user_id == user.id)
    )
    if existing_preference_id is not None:
        raise OnboardingAlreadyCompletedError

    preference = Preference(
        user_id=user.id,
        crypto_assets=list(onboarding_data.crypto_assets),
        investor_type=onboarding_data.investor_type,
        content_preferences=list(onboarding_data.content_preferences),
    )

    try:
        db.add(preference)
        user.onboarding_completed = True
        db.commit()
        db.refresh(preference)
        db.refresh(user)
        return preference
    except IntegrityError as exc:
        db.rollback()
        if getattr(exc.orig, "sqlstate", None) == "23505":
            raise OnboardingAlreadyCompletedError from exc
        raise OnboardingPersistenceError from exc
    except SQLAlchemyError as exc:
        db.rollback()
        raise OnboardingPersistenceError from exc


def get_user_preferences(db: Session, user_id: int) -> Preference | None:
    return db.scalar(select(Preference).where(Preference.user_id == user_id))
