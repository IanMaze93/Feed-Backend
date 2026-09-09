from datetime import datetime

from bson import ObjectId
from pydantic import BaseModel, ConfigDict, Field

from src.models.database.common import ObjectIdString


class User(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
    )

    id: ObjectId = Field(default_factory=ObjectId, alias="_id")
    firstName: str
    lastName: str
    email: str
    username: str
    passwordHash: str
    createdAt: datetime
    updatedAt: datetime


class Outbound_User(User):
    id: ObjectIdString = Field(alias="_id")
    username: str
    firstName: str
    lastName: str
    email: str
    createdAt: datetime
    updatedAt: datetime
