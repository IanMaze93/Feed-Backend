from datetime import datetime

from bson import ObjectId
from pydantic import BaseModel, ConfigDict, Field, field_validator


class Pointer(BaseModel):
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
    pointers: list[Pointer] = Field(default_factory=list)
    createdAt: datetime
    updatedAt: datetime


class Outbound_Topic(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
    )

    id: str = Field(alias="_id")
    userId: str
    topic: str
    pointers: list[Pointer] = Field(default_factory=list)
    createdAt: datetime
    updatedAt: datetime

    @field_validator("id", "userId", mode="before")
    @classmethod
    def object_id_to_string(cls, value):
        if isinstance(value, ObjectId):
            return str(value)

        return value


class Outbound_Topics(BaseModel):
    topics: list[Outbound_Topic] = Field(default_factory=list)
