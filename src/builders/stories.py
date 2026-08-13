from datetime import datetime

from bson import ObjectId
from pydantic import BaseModel, ConfigDict

from src.models.database.story import Story


class StoryBuilderPayload(BaseModel):
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
    )

    title: str
    link: str
    feed_type: str
    pointer_id: ObjectId
    published: datetime | None = None


def build_stories(payload: StoryBuilderPayload) -> Story:
    return Story(
        id=ObjectId(),
        title=payload.title,
        link=payload.link,
        source=payload.feed_type,
        published_at=payload.published,
        pointer_id=payload.pointer_id,
    )
