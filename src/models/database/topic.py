from datetime import datetime

from bson import ObjectId
from pydantic import BaseModel, ConfigDict, Field

from src.models.database.common import ObjectIdString


class Topic(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
    )

    id: ObjectId = Field(default_factory=ObjectId, alias="_id")
    userId: ObjectId
    topic: str
    pointers: list[ObjectId] = Field(default_factory=list)
    createdAt: datetime
    updatedAt: datetime


class Outbound_Topic(Topic):
    id: ObjectIdString = Field(alias="_id")
    userId: ObjectIdString
    pointers: list[ObjectIdString] = Field(default_factory=list)


class Outbound_Topics(BaseModel):
    topics: list[Outbound_Topic] = Field(default_factory=list)
