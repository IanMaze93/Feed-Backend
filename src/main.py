from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException

from src.builders.users import build_user
from src.cron.scheduler import getScheduler
from src.database.mongo_client import connectToDatabase
from src.database.stories import get_all_stories_by_user
from src.database.topics import (
    add_pointer_to_topic,
    get_all_topics_by_user_id,
)
from src.handlers.auth import login_handler
from src.handlers.common import createEntity, deleteEntityById
from src.handlers.health import health_handler
from src.handlers.root import root_handler
from src.handlers.stories import get_stories
from src.handlers.topics import create_topic_handler
from src.handlers.users import get_user_by_id
from src.models.api.stories import AllStoriesResponse
from src.models.api.topic import CreateTopicRequest, PointerPayload
from src.models.api.user import LoginPayload, SignupPayload
from src.models.database.common import Collections
from src.models.database.story import Outbound_Stories, Outbound_Story
from src.models.database.topic import Outbound_Topic
from src.setup.mongo.index import create_indexes

scheduler = getScheduler()

db = connectToDatabase()


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_indexes(db)
    scheduler.start()

    yield

    scheduler.shutdown()


app = FastAPI(
    title="Feed Backend API",
    version="0.1.0",
    description="Core API gateway for Feed services.",
    lifespan=lifespan,
)


@app.get("/health")
def health():
    return health_handler()


@app.get("/")
def root():
    return root_handler()


@app.post("/auth/login")
def login(payload: LoginPayload):
    user_id = login_handler(payload)
    if not user_id:
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password",
        )
    return {"user_id": user_id}


@app.post("/users")
def create_user(payload: SignupPayload):
    return createEntity(
        data=build_user(payload),
        collection=Collections.USERS,
    )


@app.get("/users/{user_id}")
def get_user(user_id: str):
    return get_user_by_id(user_id)


@app.post("/users/{user_id}/topics")
def create_topic(user_id: str, payload: CreateTopicRequest) -> Outbound_Topic:
    return create_topic_handler(user_id=user_id, payload=payload)


@app.post("/users/{user_id}/topics/{topic_id}/delete")
def delete_topic(topic_id: str):
    return deleteEntityById(entity_id=topic_id, collection=Collections.TOPICS)


@app.post("/users/{user_id}/topics/{topic_id}/pointers")
def add_pointer(user_id: str, topic_id: str, payload: PointerPayload):
    return add_pointer_to_topic(user_id=user_id, topic_id=topic_id, pointer=payload)


@app.post("/pointers/{pointer_id}/delete")
def delete_pointer(pointer_id: str):
    return deleteEntityById(entity_id=pointer_id, collection=Collections.POINTERS)


@app.get("/users/{user_id}/topics")
def get_topics(user_id: str):
    return get_all_topics_by_user_id(user_id)


@app.get("/users/{user_id}/topics/{topic_id}/stories")
def get_stories_by_topic(user_id: str, topic_id: str) -> Outbound_Stories:
    stories = get_stories(
        user_id=user_id,
        topic_id=topic_id,
    )

    return Outbound_Stories(
        stories=[Outbound_Story.model_validate(story.model_dump()) for story in stories]
    )


@app.get("/users/{user_id}/stories")
def get_stories_by_user(user_id: str) -> AllStoriesResponse:
    return get_all_stories_by_user(user_id)
