from pydantic import BaseModel

from src.models.database.story import Outbound_Stories


class TopicResponse(BaseModel):
    topic: str
    entries: list[Outbound_Stories] = []


class AllStoriesResponse(BaseModel):
    stories: list[TopicResponse] = []
