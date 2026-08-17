from src.database.topics import get_all_topics_by_user_id
from src.handlers.stories import get_stories
from src.models.api.stories import AllStoriesResponse, TopicResponse
from src.models.database.story import Outbound_Story


def get_all_stories_by_user(user_id: str) -> AllStoriesResponse:
    response = get_all_topics_by_user_id(user_id)

    stories = []

    for topic in response.topics:
        topic_stories = get_stories(
            user_id=user_id,
            topic_id=topic.id,
        )

        stories.append(
            TopicResponse(
                topic=topic.topic,
                entries=[
                    Outbound_Story.model_validate(story.model_dump())
                    for story in topic_stories
                ],
            )
        )

    return AllStoriesResponse(stories=stories)
