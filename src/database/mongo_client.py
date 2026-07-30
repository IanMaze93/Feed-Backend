import os
from typing import Collection

from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.database import Database

from src.models.database.common import Collections, DataBaseName

load_dotenv()

client: MongoClient | None = None
database: Database | None = None


def getClient() -> MongoClient:
    global client

    if client is None:
        uri = os.getenv("MONGO_URI")
        client = MongoClient(uri)

    return client


def getCollection(collectionName: Collections) -> Collection:
    database = connectToDatabase()
    return database[collectionName.value]


def connectToDatabase() -> Database:
    global database

    if database is None:
        database = getClient()[DataBaseName.EIGHT_BIT.value]

    return database
