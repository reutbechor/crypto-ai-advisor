from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies.auth import get_current_user
from app.core.security import create_access_token
from app.db.session import get_db
from app.models.user import User
from app.schemas.auth import (
    AuthUserResponse,
    LoginRequest,
    LoginResponse,
    SignupRequest,
    SignupResponse,
)
from app.services.auth import (
    EmailAlreadyExistsError,
    UserCreationError,
    authenticate_user,
    create_user,
)


router = APIRouter(prefix="/auth", tags=["Authentication"])


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


@router.post(
    "/login",
    response_model=LoginResponse,
    summary="Sign in and receive an access token",
)
def login(login_data: LoginRequest, db: Session = Depends(get_db)) -> LoginResponse:
    user = authenticate_user(db, login_data)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return LoginResponse(
        access_token=create_access_token(str(user.id)),
        user=AuthUserResponse.model_validate(user),
    )


@router.get(
    "/me",
    response_model=AuthUserResponse,
    summary="Return the authenticated user",
)
def read_current_user(
    current_user: User = Depends(get_current_user),
) -> AuthUserResponse:
    return AuthUserResponse.model_validate(current_user)
