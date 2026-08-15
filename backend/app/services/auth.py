from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.models.user import User
from app.schemas.auth import SignupRequest


class EmailAlreadyExistsError(Exception):
    pass


class UserCreationError(Exception):
    pass


def create_user(db: Session, signup_data: SignupRequest) -> User:
    try:
        existing_user_id = db.scalar(
            select(User.id).where(User.email == signup_data.email)
        )
        if existing_user_id is not None:
            raise EmailAlreadyExistsError

        user = User(
            name=signup_data.name,
            email=str(signup_data.email),
            password_hash=hash_password(signup_data.password),
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    except EmailAlreadyExistsError:
        raise
    except IntegrityError as exc:
        db.rollback()
        if getattr(exc.orig, "sqlstate", None) == "23505":
            raise EmailAlreadyExistsError from exc
        raise UserCreationError from exc
    except SQLAlchemyError as exc:
        db.rollback()
        raise UserCreationError from exc
