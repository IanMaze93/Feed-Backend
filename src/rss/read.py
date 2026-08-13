from datetime import datetime, timezone

import feedparser
from bson import ObjectId

from src.builders.stories import StoryBuilderPayload, build_stories
from src.models.database.story import Story
from src.models.rss.common import RSS_FEEDS


def rss_read(
    url: str,
    feed_type: RSS_FEEDS,
    pointer_id: ObjectId,
) -> list[Story]:
    feed = feedparser.parse(url)
    entries = feed.entries

    if not entries:
        raise ValueError(
            f"No entries found in RSS feed at {url}. "
            f"status={getattr(feed, 'status', None)}, "
            f"bozo={getattr(feed, 'bozo', None)}, "
            f"error={getattr(feed, 'bozo_exception', None)}"
        )

    stories = list(entries)

    match feed_type:
        case RSS_FEEDS.REDDIT:
            reddit_stories = stories[2:]

            parsed_stories = []

            for story in reddit_stories:
                published_parsed = getattr(
                    story,
                    "published_parsed",
                    None,
                )

                if published_parsed is None:
                    published_parsed = getattr(
                        story,
                        "updated_parsed",
                        None,
                    )

                parsed_stories.append(
                    build_stories(
                        StoryBuilderPayload(
                            title=story.get("title"),
                            link=story.get("link"),
                            pointer_id=pointer_id,
                            feed_type=feed_type.value,
                            published=(
                                datetime(
                                    *published_parsed[:6],
                                    tzinfo=timezone.utc,
                                )
                                if published_parsed
                                else None
                            ),
                        )
                    )
                )

        case RSS_FEEDS.GOOGLE:
            parsed_stories = [
                build_stories(
                    StoryBuilderPayload(
                        title=story.get("title"),
                        link=story.get("link"),
                        pointer_id=pointer_id,
                        feed_type=feed_type.value,
                        published=(
                            datetime(
                                *story.published_parsed[:6],
                                tzinfo=timezone.utc,
                            )
                            if getattr(story, "published_parsed", None)
                            else None
                        ),
                    )
                )
                for story in stories
            ]

        case _:
            raise ValueError(f"Unsupported feed type: {feed_type}")

    return parsed_stories
