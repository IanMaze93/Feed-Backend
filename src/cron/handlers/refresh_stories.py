import time
from datetime import datetime, timedelta

from src.database.create import createDocument
from src.database.delete import delete_many
from src.database.pointers import find_pointers_to_refresh
from src.database.update import update_one
from src.models.database.common import Collections
from src.models.rss.common import RSS_FEEDS
from src.rss.read import rss_read
from src.tools.logging import getLogger

logger = getLogger()

REFRESH_DELAYS = {
    RSS_FEEDS.REDDIT: 60,
    RSS_FEEDS.GOOGLE: 10,
}

FAILURE_RETRY_DELAY = timedelta(minutes=30)


def refresh_stories():
    pointers_to_refresh = find_pointers_to_refresh()

    if not pointers_to_refresh:
        logger.info("No pointers need refreshing.")
        return

    for pointer in pointers_to_refresh:
        feed_type = RSS_FEEDS(pointer.feed_type)

        try:
            stories = rss_read(
                url=pointer.url,
                feed_type=feed_type,
                pointer_id=pointer.id,
            )

            delete_many(
                collectionName=Collections.STORIES,
                query={
                    "pointer_id": pointer.id,
                },
            )

            for story in stories:
                createDocument(
                    data=story,
                    collectionName=Collections.STORIES,
                )

            now = datetime.now()

            update_one(
                Collections.POINTERS,
                {"_id": pointer.id},
                {
                    "$set": {
                        "last_fetched": now,
                        "next_fetch": now + timedelta(hours=24),
                        "updated_at": now,
                    }
                },
            )

            logger.info(
                "Successfully refreshed pointer %s with %s stories",
                pointer.id,
                len(stories),
            )

        except Exception:
            logger.exception(
                "Failed to refresh stories for pointer %s",
                pointer.id,
            )

            now = datetime.now()

            update_one(
                Collections.POINTERS,
                {"_id": pointer.id},
                {
                    "$set": {
                        "next_fetch": now + FAILURE_RETRY_DELAY,
                        "updated_at": now,
                    }
                },
            )

        finally:
            delay = REFRESH_DELAYS.get(feed_type, 10)

            logger.info(
                "Waiting %s seconds before processing next pointer",
                delay,
            )

            time.sleep(delay)
