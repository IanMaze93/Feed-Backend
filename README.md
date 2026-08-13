# Feed Backend

Backend API for **Feed**, a personalized news aggregation platform built with FastAPI and MongoDB.

Users create topics and attach feed pointers to those topics. Pointers represent external RSS/Atom feeds such as Reddit or Google News. Stories are fetched in the background and stored in MongoDB so API requests do not need to fetch external feeds in real time.

---

# Architecture

The core data model consists of three resources:

```text
User
 └── Topic
      └── Pointer IDs
           ↓
        Pointer
           ↓
        Stories
```

## Topics

A topic is a user-defined collection of feeds.

Examples:

```text
UAP
Marvel
Artificial Intelligence
Python
```

Topics belong to individual users.

A topic does **not** directly own its stories. Instead, it stores references to one or more pointers.

Example:

```json
{
  "_id": "...",
  "userId": "...",
  "topic": "Marvel",
  "pointers": ["...", "..."]
}
```

This allows users to organize feeds however they want without duplicating the underlying feed data.

---

## Pointers

A pointer represents a unique external feed.

Examples:

```text
https://www.reddit.com/r/UFOs.rss
https://www.reddit.com/r/MarvelStudiosSpoilers.rss
Google News RSS feeds
```

Pointers are shared resources.

If multiple users or topics subscribe to the same feed, they reference the **same pointer** instead of creating duplicate pointers.

```text
User A Topic ──┐
               ├── Pointer ── Stories
User B Topic ──┘
```

This means the backend only needs to fetch an external feed once.

Pointers contain scheduling information used by the background refresh system:

```text
url
normalized_url
feed_type
last_fetched
next_fetch
created_at
updated_at
```

Before creating a pointer, the backend normalizes its URL and checks whether that pointer already exists.

---

## Stories

Stories belong to pointers.

```text
Pointer
   │
   ├── Story
   ├── Story
   ├── Story
   └── Story
```

A story contains information such as:

```text
pointer_id
title
link
source
published_at
```

`source` identifies where the story originated, such as:

```text
reddit
google
```

`published_at` may be `null` when the source feed does not provide a publication timestamp.

Stories are stored in MongoDB rather than fetched when a user requests their feed.

---

# Feed Retrieval

When a user requests stories for a topic:

```text
Topic
  ↓
Pointer IDs
  ↓
Stories matching those pointer IDs
  ↓
API Response
```

Conceptually, the MongoDB query is:

```python
{
    "pointer_id": {
        "$in": topic.pointers
    }
}
```

This avoids making external RSS requests during normal API requests.

---

# Background Refresh System

Feed fetching happens independently from API requests.

APScheduler periodically runs the story refresh job.

```text
APScheduler
     ↓
Find pointers ready for refresh
     ↓
Fetch RSS/Atom feed
     ↓
Parse stories
     ↓
Replace stored stories
     ↓
Update pointer schedule
```

A pointer is ready for refresh when:

```text
next_fetch is None
```

or:

```text
next_fetch <= current time
```

After a successful refresh:

```text
last_fetched = now
next_fetch = now + refresh interval
```

A delay is placed between external feed requests to reduce the chance of hitting provider rate limits.

Failures for one pointer should not prevent other pointers from refreshing.

---

# Pointer Deduplication

Pointers are deduplicated globally by their normalized URL.

Before creating a pointer:

```text
Incoming URL
    ↓
Normalize URL
    ↓
Search MongoDB
    ↓
Exists?
   /     \
 yes      no
  ↓        ↓
reuse    create
  │        │
  └── ID ──┘
      ↓
Add pointer ID to topic
```

This is intentionally different from deduplicating topic names.

For example:

```text
"UAP"
"UAP News"
"UFO News"
"Aliens"
```

may represent similar concepts, but users are free to organize and name their topics however they want.

The important shared resource is the **pointer**, not the topic name.

---

# MongoDB Indexes

Indexes are created during FastAPI application startup using the application lifespan handler.

Example:

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    create_indexes(db)
    scheduler.start()

    yield

    scheduler.shutdown()
```

Useful indexes include:

### Unique pointer URLs

```python
collection.create_index(
    "normalized_url",
    unique=True,
)
```

This prevents duplicate pointers from being stored.

### Pointer refresh scheduling

```python
collection.create_index("next_fetch")
```

This improves queries that find pointers ready to refresh.

### Stories by pointer

```python
collection.create_index("pointer_id")
```

This improves story retrieval and deletion by pointer.

### Topics by user

```python
collection.create_index("userId")
```

This improves retrieving all topics belonging to a user.

Indexes should enforce database-level guarantees where appropriate rather than relying exclusively on application-level checks.

---

# Database Models vs API Models

MongoDB uses `ObjectId` values internally.

For example:

```python
class Story(BaseModel):
    id: ObjectId = Field(
        default_factory=ObjectId,
        alias="_id",
    )

    pointer_id: ObjectId
```

API responses must convert these values into strings because MongoDB `ObjectId` values cannot be serialized directly to JSON.

Outbound models handle this conversion:

```python
class Outbound_Story(Story):
    id: ObjectIdString = Field(alias="_id")
    pointer_id: ObjectIdString
```

The intended separation is:

```text
MongoDB
   ↓
Database Model
   ↓
Internal application logic
   ↓
Outbound Model
   ↓
FastAPI
   ↓
JSON
```

Internal database and handler functions can work with models such as:

```text
User
Topic
Pointer
Story
```

The API layer converts these into:

```text
Outbound_User
Outbound_Topic
Outbound_Pointer
Outbound_Story
```

before returning them to clients.

---

# Getting Started

## Install Dependencies

```bash
poetry install
```

## Install Git Hooks

```bash
poetry run pre-commit install
```

---

# Development

Run the API:

```bash
poetry run uvicorn src.main:app --reload
```

Run the test suite:

```bash
poetry run pytest
```

Run linting:

```bash
poetry run ruff check .
```

Format the project:

```bash
poetry run ruff format .
```

Run all pre-commit hooks:

```bash
poetry run pre-commit run --all-files
```

---

# Docker

Start all configured services:

```bash
docker compose up --build
```

Run in the background:

```bash
docker compose up --build -d
```

Stop all services:

```bash
docker compose down
```

View logs:

```bash
docker compose logs -f
```

View API logs:

```bash
docker compose logs -f feed-api
```

---

# Current Feed Sources

The feed parser currently supports:

- Reddit RSS/Atom feeds
- Google News RSS feeds

Each feed source is normalized into the common Story model so clients do not need to understand the differences between individual RSS providers.

---

# Design Goals

The backend is designed around a few core principles:

- **Fetch once, reuse many times** — shared pointers prevent duplicate external requests.
- **Keep user organization flexible** — topic names do not need global normalization or deduplication.
- **Separate fetching from reading** — users read stories from MongoDB rather than waiting for external RSS requests.
- **Respect external services** — scheduled refreshes and delays reduce unnecessary requests.
- **Database-enforced uniqueness** — MongoDB indexes protect against duplicate shared resources.
- **Separate internal and external models** — MongoDB-specific types remain inside the backend while API responses remain JSON-friendly.
