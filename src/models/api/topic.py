from bson import ObjectId
from pydantic import BaseModel, ConfigDict, Field


class PointerPayload(BaseModel):
    url: str
    feed_type: str


class CreateTopicRequest(BaseModel):
    topic: str
    pointers: list[PointerPayload] = Field(default_factory=list)


class CreateTopicPayload(BaseModel):
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
    )

    userId: str
    topic: str
    pointers: list[ObjectId] = Field(default_factory=list)


class UpdateTopicPayload(BaseModel):
    id: str | None = None
    topic: str
    pointers: list[PointerPayload] = Field(default_factory=list)


class UpdateTopicsRequest(BaseModel):
    topics: list[UpdateTopicPayload] = Field(default_factory=list)
