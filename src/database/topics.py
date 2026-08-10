from datetime import datetime

from bson import ObjectId
from bson.errors import InvalidId

from src.database.find import find_many, find_one
from src.database.update import update_one
from src.models.database.common import Collections
from src.models.database.topic import Outbound_Topic, Outbound_Topics, Topic
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
            "userId": user_object_id,
            "topic": topic["topic"],
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

        return Outbound_Topic.model_validate(find_one(Collections.TOPICS, query))

    except InvalidId as error:
        raise ValueError("Invalid user ID or topic ID.") from error

    except Exception as error:
        logger.exception("Error adding pointer to topic")
        raise ValueError(f"Error adding pointer to topic: {error}") from error


def get_all_topics_by_user_id(user_id: str) -> Outbound_Topics:
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

        return Outbound_Topics(topics=data)

    except InvalidId as error:
        raise ValueError("Invalid user ID.") from error

    except Exception as error:
        logger.exception("Error retrieving topics")
        raise ValueError(f"Error retrieving topics: {error}") from error


def get_topic_by_id(topic_id: str) -> Topic:
    """
    Get a topic by its ID.
    """
    try:
        topic_object_id = ObjectId(topic_id)

        topic = find_one(
            Collections.TOPICS,
            {"_id": topic_object_id},
        )

        if not topic:
            return None

        return topic

    except InvalidId as error:
        raise ValueError("Invalid topic ID.") from error

    except Exception as error:
        logger.exception("Error retrieving topic")
        raise ValueError(f"Error retrieving topic: {error}") from error
