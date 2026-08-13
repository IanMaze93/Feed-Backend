from asyncio.log import logger

from bson import ObjectId
from bson.errors import InvalidId

from src.database.find import find_one
from src.models.database.common import Collections
from src.models.database.user import Outbound_User


def get_user_by_id(user_id: str):
    """
    Get a user by their ID.

    Args:
        user_id (str): The ID of the user to retrieve.

    Returns:
        dict: The user data if found, otherwise None.
    """
    try:
        user_object_id = ObjectId(user_id)

        response = find_one(
            Collections.USERS,
            {"_id": user_object_id},
        )

        return Outbound_User(**response) if response else None
    except InvalidId as error:
        raise ValueError("Invalid user ID.") from error
    except Exception as error:
        logger.exception("Error retrieving user")
        raise ValueError(f"Error retrieving user: {error}") from error
