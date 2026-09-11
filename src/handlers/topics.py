from src.builders.topics import build_topic
from src.database.delete import delete_one
from src.database.mongo_client import getClient
from src.database.pointers import find_or_create_pointer
from src.database.topics import get_all_topics_by_user_id, get_topic_by_id
from src.database.update import update_one
from src.handlers.common import createEntity
from src.models.api.topic import (
    CreateTopicPayload,
    CreateTopicRequest,
    UpdateTopicsRequest,
)
from src.models.database.common import Collections
from src.models.database.topic import Outbound_Topic
from src.tools.logging import getLogger

logger = getLogger()


def update_topics_handler(
    user_id: str,
    payload: UpdateTopicsRequest,
) -> list[Outbound_Topic]:
    client = getClient()

    with client.start_session() as session:
        with session.start_transaction():
            existing_topics = get_all_topics_by_user_id(user_id)

            for incoming_topic in payload.topics:
                existing_topic = next(
                    (
                        topic
                        for topic in existing_topics
                        if str(topic.id) == str(incoming_topic.id)
                    ),
                    None,
                )

                if existing_topic:
                    pointer_ids = []

                    for pointer in incoming_topic.pointers:
                        db_pointer = find_or_create_pointer(
                            url=pointer.url,
                            feed_type=pointer.feed_type,
                        )

                        pointer_ids.append(db_pointer.id)

                    existing_topic.topic = incoming_topic.topic
                    existing_topic.pointers = pointer_ids

                    update_one(
                        Collections.TOPICS,
                        str(existing_topic.id),
                        existing_topic,
                    )

                else:
                    create_topic_handler(
                        user_id=user_id,
                        payload=CreateTopicRequest(
                            topic=incoming_topic.topic,
                            pointers=incoming_topic.pointers,
                        ),
                    )

            incoming_ids = {
                str(topic.id) for topic in payload.topics if topic.id is not None
            }

            for existing_topic in existing_topics:
                if str(existing_topic.id) not in incoming_ids:
                    delete_one(
                        Collections.TOPICS,
                        str(existing_topic.id),
                    )

            return get_all_topics_by_user_id(user_id)


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
