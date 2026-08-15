import bcrypt


def hash_password(password: str) -> str:
    password_bytes = password.encode("utf-8")
    if len(password_bytes) > 72:
        raise ValueError("Password must not exceed 72 bytes.")

    return bcrypt.hashpw(password_bytes, bcrypt.gensalt()).decode("utf-8")
