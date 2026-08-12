from src.database.topics import get_all_topics_by_user_id
from src.handlers.stories import get_stories
from src.models.database.story import Outbound_Stories, Outbound_Story


def get_all_stories_by_user(user_id: str) -> Outbound_Stories:
    response = get_all_topics_by_user_id(user_id)

    stories = []

    for topic in response.topics:
        topic_stories = get_stories(user_id=user_id, topic_id=topic.id)

        stories.extend(Outbound_Story.model_validate(story) for story in topic_stories)

    return Outbound_Stories(stories=stories)
