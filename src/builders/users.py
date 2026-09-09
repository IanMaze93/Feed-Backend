from datetime import UTC, datetime

from bson import ObjectId

from src.models.api.user import SignupPayload
from src.models.database.user import User
from src.tools.login.password import hash_password


def build_user(payload: SignupPayload) -> User:
    now = datetime.now(UTC)

    password_hash = hash_password(payload.password)

    return User(
        id=ObjectId(),
        firstName=payload.firstName,
        lastName=payload.lastName,
        email=payload.email,
        username=payload.username,
        passwordHash=password_hash,
        createdAt=now,
        updatedAt=now,
    )
