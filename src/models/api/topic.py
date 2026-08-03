from pydantic import BaseModel

from src.models.database.topic import pointer


class CreateTopicPayload(BaseModel):
    userId: str
    topic: str
    pointers: list[pointer] = []


class CreateTopicRequest(BaseModel):
    topic: str
    pointers: list[pointer] = []
