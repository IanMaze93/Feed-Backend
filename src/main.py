from fastapi import FastAPI

from src.builders.topics import build_topic
from src.builders.users import build_user
from src.database.topics import get_all_topics_by_user_id
from src.handlers.common import createEntity, getEntityById
from src.handlers.health import health_handler
from src.handlers.root import root_handler
from src.models.api.topic import CreateTopicPayload, CreateTopicRequest
from src.models.api.user import CreateUserPayload
from src.models.database.common import Collections

app = FastAPI(
    title="Feed Backend API",
    version="0.1.0",
    description="Core API gateway for Feed services.",
)


@app.get("/health")
def health():
    return health_handler()


@app.get("/")
def root():
    return root_handler()


@app.post("/users")
def create_user(payload: CreateUserPayload):
    return createEntity(
        data=build_user(payload),
        collection=Collections.USERS,
    )


@app.get("/users/{user_id}")
def get_user(user_id: str):
    return getEntityById(user_id, collection=Collections.USERS)


@app.post("/users/{user_id}/topics")
def create_topic(user_id: str, payload: CreateTopicRequest):
    return createEntity(
        data=build_topic(
            payload=CreateTopicPayload(userId=user_id, topic=payload.topic)
        ),
        collection=Collections.TOPICS,
    )


@app.get("/users/{user_id}/topics")
def get_topics(user_id: str):
    return get_all_topics_by_user_id(user_id)
