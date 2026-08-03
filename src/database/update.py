from src.database.mongo_client import getCollection
from src.models.database.common import Collections


def update_one(collectionName: Collections, query, update):
    collection = getCollection(collectionName)
    return collection.update_one(query, update)


def update_many(collectionName: Collections, query, update):
    collection = getCollection(collectionName)
    return collection.update_many(query, update)


def upsert_one(collectionName: Collections, query, update):
    collection = getCollection(collectionName)
    return collection.update_one(query, update, upsert=True)


def upsert_many(collectionName: Collections, query, update):
    collection = getCollection(collectionName)
    return collection.update_many(query, update, upsert=True)


def push_to_array(collectionName: Collections, query, array_field, value):
    collection = getCollection(collectionName)
    update = {"$push": {array_field: value}}
    return collection.update_one(query, update)
