from datetime import datetime, timezone

import feedparser

from src.builders.stories import build_stories
from src.models.rss.common import RSS_FEEDS
from src.models.rss.story import Story


def rss_read(url: str, feed_type: RSS_FEEDS) -> list[Story]:
    feed = feedparser.parse(url)
    entries = feed.entries

    if not entries:
        raise ValueError(f"No entries found in the RSS feed at {url}")

    stories = list(entries)

    match feed_type:
        case RSS_FEEDS.REDDIT:
            parsed_stories = [
                build_stories(
                    {
                        "title": story.get("title"),
                        "link": story.get("link"),
                        "feed_type": feed_type,
                        "published": story.get("published"),
                    }
                )
                for story in stories
            ]
        case RSS_FEEDS.GOOGLE:
            parsed_stories = [
                build_stories(
                    {
                        "title": story.get("title"),
                        "link": story.get("link"),
                        "feed_type": feed_type,
                        "published": (
                            datetime(*story.published_parsed[:6], tzinfo=timezone.utc)
                            if getattr(story, "published_parsed", None)
                            else None
                        ),
                    }
                )
                for story in stories
            ]
        case _:
            raise ValueError(f"Unsupported feed type: {feed_type}")

    # Return ids as strings instead of ObjectId
    for story in parsed_stories:
        story.id = str(story.id)

    return parsed_stories
