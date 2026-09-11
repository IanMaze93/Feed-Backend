from src.database.mongo_client import getCollection
from src.models.database.common import Collections


def update_one(collectionName: Collections, query, update, session=None):
    collection = getCollection(collectionName)
    return collection.update_one(query, update, session=session)


def update_many(collectionName: Collections, query, update, session=None):
    collection = getCollection(collectionName)
    return collection.update_many(query, update, session=session)


def upsert_one(collectionName: Collections, query, update, session=None):
    collection = getCollection(collectionName)
    return collection.update_one(query, update, upsert=True, session=session)


def upsert_many(collectionName: Collections, query, update, session=None):
    collection = getCollection(collectionName)
    return collection.update_many(query, update, upsert=True, session=session)


def push_to_array(collectionName: Collections, query, array_field, value, session=None):
    collection = getCollection(collectionName)
    update = {"$push": {array_field: value}}
    return collection.update_one(query, update, session=session)
