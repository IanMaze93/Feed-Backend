from bson import ObjectId

from src.database.create import createDocument
from src.database.find import find_one
from src.models.database.common import Collections
from src.tools.logging import getLogger

logger = getLogger()


def getEntityById(entity_id: str, collection: Collections):
    try:
        entity = find_one(collection, {"_id": ObjectId(entity_id)})
        if entity is None:
            return None

        entity["_id"] = str(entity["_id"])
        return {"entity": entity}
    except Exception as e:
        logger.exception("Error retrieving entity", exc_info=True)
        raise ValueError(f"Error retrieving entity: {e}")


def createEntity(data: dict, collection: Collections):
    try:
        entity_id = createDocument(collection, data)
        return entity_id

    except Exception as e:
        logger.exception("Error creating entity", exc_info=True)
        raise ValueError(f"Error creating entity: {e}")


def deleteEntityById(entity_id: str, collection: Collections):
    try:
        from src.database.delete import delete_one

        result = delete_one(collection, {"_id": ObjectId(entity_id)})
        if result.deleted_count == 0:
            return {"status": "not found"}
        return {"status": "success"}
    except Exception as e:
        logger.exception("Error deleting entity", exc_info=True)
        raise ValueError(f"Error deleting entity: {e}")
