from src.database.find import find_one
from src.models.api.user import LoginPayload
from src.models.database.common import Collections
from src.models.database.user import User
from src.tools.logging import getLogger
from src.tools.login.password import verify_password

logger = getLogger()


def login_handler(payload: LoginPayload) -> str | None:
    try:
        response = find_one(
            Collections.USERS,
            {"username": payload.username},
        )

        user = User(**response) if response else None

        if not user:
            return None

        is_valid_password = verify_password(payload.password, user.passwordHash)

        if not is_valid_password:
            return None

        return str(user.id)

    except Exception as error:
        logger.exception("Error logging in user: %s", error)
        raise ValueError(f"Error logging in user: {error}") from error
