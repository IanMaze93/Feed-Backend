from src.database.topics import get_topic_by_id
from src.models.database.topic import Topic
from src.models.rss.common import RSS_FEEDS
from src.rss.read import rss_read
from src.tools.logging import getLogger

logger = getLogger()


def get_stories(user_id: str, topic_id: str):
    topic_data = get_topic_by_id(topic_id)

    logger.info(f"Retrieved topic data for topic_id {topic_id}, user_id {user_id}")

    topic: Topic = topic_data
    stories = []
    pointers = topic.get("pointers", [])

    try:
        for pointer in pointers:
            stories.extend(
                rss_read(
                    url=pointer.get("link"),
                    feed_type=RSS_FEEDS(pointer.get("feed_type")),
                )
            )
    except Exception as e:
        logger.exception("Error retrieving stories", exc_info=True)
        raise ValueError(f"Error retrieving stories: {e}")

    return stories
