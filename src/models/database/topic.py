from datetime import datetime

from bson import ObjectId
from pydantic import BaseModel, ConfigDict, Field


class pointer(BaseModel):
    link: str
    feed_type: str


class Topic(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
    )

    id: ObjectId = Field(default_factory=ObjectId, alias="_id")
    userId: ObjectId
    topic: str
    pointers: list[pointer] = []
    createdAt: datetime
    updatedAt: datetime


class Outbound_Topic(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
    )

    id: str = Field(default_factory=str, alias="_id")
    userId: str
    topic: str
    pointers: list[pointer] = []
    createdAt: datetime
    updatedAt: datetime


class Outbound_Topics(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
    )

    topics: list[Outbound_Topic] = []
