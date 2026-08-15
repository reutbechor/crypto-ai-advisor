from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.auth import SignupRequest, SignupResponse
from app.services.auth import (
    EmailAlreadyExistsError,
    UserCreationError,
    create_user,
)


router = APIRouter(prefix="/auth", tags=["Signup"])


@router.post(
    "/signup",
    response_model=SignupResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a user account",
)
def signup(signup_data: SignupRequest, db: Session = Depends(get_db)) -> SignupResponse:
    try:
        user = create_user(db, signup_data)
    except EmailAlreadyExistsError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists.",
        ) from exc
    except UserCreationError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to create account.",
        ) from exc

    return SignupResponse.model_validate(user)
