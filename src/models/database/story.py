from datetime import datetime

from bson import ObjectId
from pydantic import BaseModel, ConfigDict, Field

from src.models.database.common import ObjectIdString


class Story(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
    )

    id: ObjectId = Field(default_factory=ObjectId, alias="_id")
    pointer_id: ObjectId
    title: str
    link: str
    source: str
    published_at: datetime | None = None


class Outbound_Story(Story):
    id: ObjectIdString = Field(alias="_id")
    pointer_id: ObjectIdString


class Outbound_Stories(BaseModel):
    stories: list[Outbound_Story] = Field(default_factory=list)
