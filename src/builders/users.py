from datetime import UTC, datetime

from bson import ObjectId

from src.models.api.user import CreateUserPayload
from src.models.database.user import User


def build_user(payload: CreateUserPayload) -> User:
    now = datetime.now(UTC)

    return User(
        id=ObjectId(),
        firstName=payload.firstName,
        lastName=payload.lastName,
        email=payload.email,
        createdAt=now,
        updatedAt=now,
    )
