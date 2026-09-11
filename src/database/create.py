from typing import TypeVar

from bson import ObjectId
from pydantic import BaseModel

from src.database.mongo_client import getCollection
from src.models.database.common import Collections
from src.tools.logging import getLogger

T = TypeVar("T", bound=BaseModel)

logger = getLogger()


def createDocument(collectionName: Collections, data: T, session=None) -> ObjectId:
    collection = getCollection(collectionName)

    try:
        response = collection.insert_one(
            data.model_dump(by_alias=True, exclude_none=True),
            session=session,
        )

        logger.info(
            "Record Created collection=%s id=%s",
            collectionName,
            response.inserted_id,
        )

        return str(response.inserted_id)
    except Exception as error:
        logger.exception(
            "Error creating record",
            {"collectionName": collectionName, "data": data, "error": error},
        )

        raise ValueError("Error creating record") from error
