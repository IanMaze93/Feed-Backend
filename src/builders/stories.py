from bson import ObjectId

from src.models.rss.story import Story


def build_stories(payload: dict) -> Story:
    return Story(
        id=ObjectId(),
        title=payload.get("title"),
        link=payload.get("link"),
        feed_type=payload.get("feed_type"),
        created_at=payload.get("published"),
    )
