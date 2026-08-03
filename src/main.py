from fastapi import FastAPI

from src.builders.topics import build_topic
from src.builders.users import build_user
from src.database.topics import add_pointer_to_topic, get_all_topics_by_user_id
from src.handlers.common import createEntity, getEntityById
from src.handlers.health import health_handler
from src.handlers.root import root_handler
from src.models.api.topic import CreateTopicPayload, CreateTopicRequest
from src.models.api.user import CreateUserPayload
from src.models.database.common import Collections
from src.models.rss.common import RSS_FEEDS
from src.rss.read import rss_read

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
            payload=CreateTopicPayload(
                userId=user_id, topic=payload.topic, pointers=payload.pointers
            )
        ),
        collection=Collections.TOPICS,
    )


@app.post("/users/{user_id}/topics/{topic_id}/pointers")
def add_pointer(user_id: str, topic_id: str, payload: dict):
    return add_pointer_to_topic(user_id=user_id, topic_id=topic_id, pointer=payload)


@app.get("/users/{user_id}/topics")
def get_topics(user_id: str):
    return get_all_topics_by_user_id(user_id)


@app.get("/users/{user_id}/topics/{topic_id}/stories")
def get_stories(user_id: str, topic_id: str):
    # Implement the logic to get stories for the given topic_id
    print(f"Fetching stories for user_id: {user_id}, topic_id: {topic_id}")
    return rss_read(
        "https://news.google.com/rss/search?q=marvel-news", feed_type=RSS_FEEDS.GOOGLE
    )
