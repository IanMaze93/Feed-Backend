from pydantic import BaseModel, Field

from src.models.database.topic import Pointer


class CreateTopicPayload(BaseModel):
    userId: str
    topic: str
    pointers: list[Pointer] = Field(default_factory=list)


class CreateTopicRequest(BaseModel):
    topic: str
    pointers: list[Pointer] = Field(default_factory=list)
