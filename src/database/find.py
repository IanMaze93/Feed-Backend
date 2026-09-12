from src.database.mongo_client import getCollection
from src.models.database.common import Collections


def find_one(
    collection_name: Collections,
    query: dict,
    session=None,
):
    collection = getCollection(collection_name)

    if session is None:
        return collection.find_one(query)

    return collection.find_one(query, session=session)


def find_many(
    collection_name: Collections,
    query: dict,
    session=None,
):
    collection = getCollection(collection_name)

    if session is None:
        return collection.find(query)

    return collection.find(query, session=session)
