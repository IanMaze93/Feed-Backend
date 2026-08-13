from datetime import UTC, datetime

from bson import ObjectId
from pydantic.v1 import BaseModel

from src.models.database.pointer import Pointer


class PointerBuilderPayload(BaseModel):
    url: str
    normalized_url: str
    feed_type: str


def build_pointer(payload: PointerBuilderPayload) -> Pointer:
    now = datetime.now(UTC)

    return Pointer(
        id=ObjectId(),
        url=payload.url,
        normalized_url=payload.normalized_url,
        feed_type=payload.feed_type,
        last_fetched=None,
        next_fetch=None,
        created_at=now,
        updated_at=now,
    )
