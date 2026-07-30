from src.database.mongo_client import getCollection
from src.models.database.common import Collections


def find_one(collectionName: Collections, query):
    collection = getCollection(collectionName)
    return collection.find_one(query)


def find_many(collectionName: Collections, query):
    collection = getCollection(collectionName)
    return collection.find(query)
