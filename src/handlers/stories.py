from src.database.find import find_many
from src.database.topics import get_topic_by_id
from src.models.database.common import Collections
from src.models.database.story import Story
from src.tools.logging import getLogger

logger = getLogger()


def get_stories(user_id: str, topic_id: str) -> list[Story]:
    try:
        topic = get_topic_by_id(topic_id)

        if topic is None:
            raise ValueError("Topic not found.")

        if str(topic.userId) != user_id:
            raise ValueError("Topic does not belong to user.")

        if not topic.pointers:
            return []

        results = find_many(
            Collections.STORIES,
            {
                "pointer_id": {
                    "$in": topic.pointers,
                }
            },
        )

        return [Story.model_validate(result) for result in results]

    except Exception as error:
        logger.exception("Error retrieving stories")
        raise ValueError(f"Error retrieving stories: {error}") from error
