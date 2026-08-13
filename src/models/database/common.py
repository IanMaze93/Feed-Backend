from enum import Enum
from typing import Annotated

from bson import ObjectId
from pydantic import BeforeValidator


class Collections(Enum):
    USERS = "Users"
    TOPICS = "Topics"
    STORIES = "Stories"
    POINTERS = "Pointers"


class DataBaseName(Enum):
    FEED_DB = "feed_db"


def object_id_to_string(value):
    if isinstance(value, ObjectId):
        return str(value)

    return value


ObjectIdString = Annotated[
    str,
    BeforeValidator(object_id_to_string),
]
