from pydantic import BaseModel

from src.models.database.story import Outbound_Story


class TopicResponse(BaseModel):
    topic: str
    entries: list[Outbound_Story] = []


class AllStoriesResponse(BaseModel):
    stories: list[TopicResponse] = []
