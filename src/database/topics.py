from datetime import datetime

from bson import ObjectId
from bson.errors import InvalidId

from src.database.find import find_many, find_one
from src.database.update import update_one
from src.models.database.common import Collections
from src.tools.logging import getLogger

logger = getLogger()


def add_pointer_to_topic(
    user_id: str,
    topic_id: str,
    pointer: dict,
) -> dict:
    try:
        user_object_id = ObjectId(user_id)
        topic_object_id = ObjectId(topic_id)

        query = {
            "_id": topic_object_id,
            "userId": user_object_id,
        }

        topic = find_one(Collections.TOPICS, query)

        pointers = topic.get("pointers", []) if topic else []

        payload = {
            "userId": str(user_object_id),
            "topic": topic["topic"] or "marvel news",
            "pointers": pointers + [pointer],
            "updatedAt": datetime.now(),
        }

        try:
            update_one(
                Collections.TOPICS,
                query,
                {"$set": payload},
            )
        except Exception as error:
            logger.exception("Error updating topic with new pointer")
            raise ValueError(
                f"Error updating topic with new pointer: {error}"
            ) from error

        return payload

    except InvalidId as error:
        raise ValueError("Invalid user ID or topic ID.") from error

    except Exception as error:
        logger.exception("Error adding pointer to topic")
        raise ValueError(f"Error adding pointer to topic: {error}") from error


def get_all_topics_by_user_id(user_id: str) -> dict:
    """
    Get all topics belonging to a user.
    """
    try:
        user_object_id = ObjectId(user_id)

        cursor = find_many(
            Collections.TOPICS,
            {"userId": user_object_id},
        )

        data = list(cursor)

        for topic in data:
            topic["_id"] = str(topic["_id"])
            topic["userId"] = str(topic["userId"])

        return {
            "status": "success",
            "entity": data,
        }

    except InvalidId as error:
        raise ValueError("Invalid user ID.") from error

    except Exception as error:
        logger.exception("Error retrieving topics")
        raise ValueError(f"Error retrieving topics: {error}") from error
