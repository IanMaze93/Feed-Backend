from datetime import datetime

from bson import ObjectId
from pydantic import BaseModel, ConfigDict, Field

from src.models.database.common import ObjectIdString


class Pointer(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
    )

    id: ObjectId = Field(default_factory=ObjectId, alias="_id")
    url: str
    normalized_url: str
    feed_type: str
    last_fetched: datetime | None = None
    next_fetch: datetime | None = None
    created_at: datetime
    updated_at: datetime


class Outbound_Pointer(Pointer):
    id: ObjectIdString


class Outbound_Pointers(BaseModel):
    pointers: list[Outbound_Pointer] = Field(default_factory=list)
