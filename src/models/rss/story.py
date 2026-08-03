from datetime import datetime

from bson import ObjectId
from pydantic import BaseModel, ConfigDict

from src.models.rss.common import RSS_FEEDS


class Story(BaseModel):
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
    )
    id: ObjectId
    title: str
    link: str
    feed_type: RSS_FEEDS
    created_at: datetime
