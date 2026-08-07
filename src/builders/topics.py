from datetime import UTC, datetime

from bson import ObjectId

from src.models.api.topic import CreateTopicPayload
from src.models.database.topic import Topic


def build_topic(payload: CreateTopicPayload) -> Topic:
    now = datetime.now(UTC)

    return Topic(
        id=ObjectId(),
        userId=ObjectId(payload.userId),
        topic=payload.topic,
        pointers=payload.pointers if hasattr(payload, "pointers") else [],
        createdAt=now,
        updatedAt=now,
    )
