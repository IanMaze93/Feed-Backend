from src.builders.topics import build_topic
from src.database.pointers import find_or_create_pointer
from src.database.topics import get_topic_by_id
from src.handlers.common import createEntity
from src.models.api.topic import CreateTopicPayload, CreateTopicRequest
from src.models.database.common import Collections
from src.models.database.topic import Outbound_Topic
from src.tools.logging import getLogger

logger = getLogger()


def create_topic_handler(
    user_id: str,
    payload: CreateTopicRequest,
) -> Outbound_Topic:
    try:
        pointer_ids = []

        for pointer in payload.pointers:
            db_pointer = find_or_create_pointer(
                url=pointer.url,
                feed_type=pointer.feed_type,
            )

            pointer_ids.append(db_pointer.id)

        created_topic_id = createEntity(
            data=build_topic(
                payload=CreateTopicPayload(
                    userId=user_id,
                    topic=payload.topic,
                    pointers=pointer_ids,
                )
            ),
            collection=Collections.TOPICS,
        )

        topic = get_topic_by_id(str(created_topic_id))

        return Outbound_Topic.model_validate(topic.model_dump())

    except Exception:
        logger.exception("Error creating topic")
        raise
