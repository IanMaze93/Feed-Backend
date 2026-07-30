from datetime import datetime

from bson import ObjectId
from pydantic import BaseModel, ConfigDict, Field


class User(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
    )

    id: ObjectId = Field(default_factory=ObjectId, alias="_id")
    firstName: str
    lastName: str
    email: str
    createdAt: datetime
    updatedAt: datetime
