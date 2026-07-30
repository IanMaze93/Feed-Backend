from pydantic import BaseModel


class CreateTopicPayload(BaseModel):
    userId: str
    topic: str


class CreateTopicRequest(BaseModel):
    topic: str
