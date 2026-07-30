import logging

from bson import ObjectId

from src.database.find import find_many
from src.models.database.common import Collections
from src.models.database.topic import Topic

logger = logging.getLogger()


def get_all_topics_by_user_id(user_id: str) -> list[Topic] | None:
    """
    Get all topics by user id.
    """
    try:
        cursor = find_many(Collections.TOPICS, {"userId": ObjectId(user_id)})
        data = list(cursor)

        if not data:
            return {"entity": None}

        for topic in data:
            topic["_id"] = str(topic["_id"])
            topic["userId"] = str(topic["userId"])

        return {"entity": data}
    except Exception as e:
        logger.exception("Error retrieving entity", exc_info=True)
        raise ValueError(f"Error retrieving entity: {e}")
