from datetime import datetime

from bson import ObjectId
from pydantic import BaseModel, ConfigDict, Field, field_validator


class Story(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
    )

    id: ObjectId = Field(default_factory=ObjectId)
    title: str
    link: str
    feed_type: str
    created_at: datetime


class Outbound_Story(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        from_attributes=True,
    )

    id: str
    title: str
    link: str
    feed_type: str
    created_at: datetime

    @field_validator("id", mode="before")
    @classmethod
    def object_id_to_string(cls, value):
        if isinstance(value, ObjectId):
            return str(value)

        return value


class Outbound_Stories(BaseModel):
    stories: list[Outbound_Story] = Field(default_factory=list)
