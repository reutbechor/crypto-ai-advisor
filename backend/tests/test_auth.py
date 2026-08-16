from sqlalchemy import select

from app.core.security import verify_password
from app.models import User


SIGNUP_PAYLOAD = {
    "name": "Test User",
    "email": "TEST@Example.COM ",
    "password": "Password123!",
}


def signup(client, **overrides):
    return client.post("/api/auth/signup", json={**SIGNUP_PAYLOAD, **overrides})


def login(client, email="test@example.com", password="Password123!"):
    return client.post(
        "/api/auth/login",
        json={"email": email, "password": password},
    )


def test_signup_normalizes_email_hashes_password_and_rejects_duplicate(client, db_session):
    created = signup(client)
    duplicate = signup(client, email="test@example.com")
    user = db_session.scalar(select(User).where(User.email == "test@example.com"))

    assert created.status_code == 201
    assert created.json()["email"] == "test@example.com"
    assert created.json()["onboarding_completed"] is False
    assert "password" not in created.json()
    assert user.password_hash != SIGNUP_PAYLOAD["password"]
    assert verify_password(SIGNUP_PAYLOAD["password"], user.password_hash)
    assert duplicate.status_code == 409


def test_login_returns_jwt_and_rejects_wrong_or_unknown_credentials(client):
    signup(client)

    success = login(client)
    wrong_password = login(client, password="WrongPassword")
    unknown_user = login(client, email="unknown@example.com")

    assert success.status_code == 200
    assert success.json()["token_type"] == "bearer"
    assert success.json()["access_token"]
    assert success.json()["user"]["email"] == "test@example.com"
    assert wrong_password.status_code == 401
    assert unknown_user.status_code == 401


def test_auth_me_accepts_valid_jwt_and_rejects_missing_invalid_or_deleted_user(
    client,
    db_session,
):
    signup(client)
    token = login(client).json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    valid = client.get("/api/auth/me", headers=headers)
    missing = client.get("/api/auth/me")
    invalid = client.get(
        "/api/auth/me",
        headers={"Authorization": "Bearer not-a-token"},
    )

    user = db_session.scalar(select(User).where(User.email == "test@example.com"))
    db_session.delete(user)
    db_session.commit()
    deleted = client.get("/api/auth/me", headers=headers)

    assert valid.status_code == 200
    assert valid.json()["email"] == "test@example.com"
    assert missing.status_code == 401
    assert invalid.status_code == 401
    assert deleted.status_code == 401
