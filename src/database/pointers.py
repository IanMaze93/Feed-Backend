from datetime import datetime

from bson import ObjectId
from bson.errors import InvalidId

from src.builders.pointers import PointerBuilderPayload, build_pointer
from src.database.find import find_many, find_one
from src.handlers.common import createEntity
from src.models.database.common import Collections
from src.models.database.pointer import Pointer
from src.tools.logging import getLogger
from src.tools.normalize.normalize_string import normalize_url

logger = getLogger()


def get_pointer_by_id(pointer_id: str) -> Pointer | None:
    """
    Get a pointer by its ID.
    """
    try:
        pointer_object_id = ObjectId(pointer_id)

        result = find_one(
            Collections.POINTERS,
            {"_id": pointer_object_id},
        )

        if result is None:
            return None

        return Pointer.model_validate(result)

    except InvalidId as error:
        raise ValueError("Invalid pointer ID.") from error

    except Exception as error:
        logger.exception("Error retrieving pointer")
        raise ValueError(f"Error retrieving pointer: {error}") from error


def get_pointer_by_url(normalized_url: str) -> Pointer | None:
    """
    Get a pointer by its normalized URL.
    """
    try:
        result = find_one(
            Collections.POINTERS,
            {"normalized_url": normalized_url},
        )

        if result is None:
            return None

        return Pointer.model_validate(result)

    except Exception as error:
        logger.exception("Error retrieving pointer by URL")
        raise ValueError(f"Error retrieving pointer by URL: {error}") from error


def find_or_create_pointer(url: str, feed_type: str) -> Pointer:
    """
    Find a pointer by its normalized URL. If it doesn't exist, create a new pointer.
    """
    try:
        normalized_url = normalize_url(url)
        pointer = get_pointer_by_url(normalized_url)

        if pointer is not None:
            return pointer

        new_pointer = build_pointer(
            payload=PointerBuilderPayload(
                url=url,
                normalized_url=normalized_url,
                feed_type=feed_type,
            )
        )

        created_pointer_id = createEntity(
            data=new_pointer,
            collection=Collections.POINTERS,
        )

        return get_pointer_by_id(str(created_pointer_id))

    except Exception as error:
        logger.exception("Error finding or creating pointer")
        raise ValueError(f"Error finding or creating pointer: {error}") from error


def find_pointers_to_refresh() -> list[Pointer]:
    """
    Find pointers that haven't been fetched in the last 24 hours or
    have never been fetched (next_fetch is None).
    """
    try:
        now = datetime.now()

        query = {
            "$or": [
                {"next_fetch": None},
                {"next_fetch": {"$lte": now}},
            ]
        }

        results = find_many(
            Collections.POINTERS,
            query,
        )

        return [Pointer.model_validate(result) for result in results]

    except Exception as error:
        logger.exception("Error finding pointers to refresh")
        raise ValueError(f"Error finding pointers to refresh: {error}") from error
