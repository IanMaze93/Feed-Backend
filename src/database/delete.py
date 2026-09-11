from src.database.mongo_client import getCollection
from src.models.database.common import Collections


def delete_one(collectionName: Collections, query, session=None):
    collection = getCollection(collectionName)
    return collection.delete_one(query, session=session)


def delete_many(collectionName: Collections, query, session=None):
    collection = getCollection(collectionName)
    return collection.delete_many(query, session=session)
