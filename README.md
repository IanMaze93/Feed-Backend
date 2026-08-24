# The Feed - Backend

<img src="./src/images/logo-feed.png">

**Your news. Your topics. No socials.**

The Feed Backend is the API and feed-processing service behind **The Feed**, a personalized news aggregator designed to give users more control over the content they see.

Instead of relying on a traditional social media feed filled with advertisements, promoted content, and algorithmic recommendations, The Feed allows users to define the topics and sources they want to follow.

Users create **topics** and attach **pointers** to external sources such as Reddit or Google News. The backend retrieves stories from those sources, stores them in MongoDB, and makes them available to The Feed frontend through the API.

The backend is built with:

- **FastAPI**
- **MongoDB**
- **APScheduler**
- **Pydantic**
- **Poetry**

Currently supported feed sources include:

- **Google News**
- **Reddit**

Additional source types can be added as the project grows.

---

# How It Works

The basic structure of The Feed is:

```text
User
  ↓
Topic
  ↓
Pointers
  ↓
Stories
```

A user creates a topic based on something they want to follow.

For example:

```text
Star Wars
DC Universe
Artificial Intelligence
Python
```

Each topic contains references to one or more **pointers**.

A pointer represents an external RSS or Atom feed:

```text
Topic: Star Wars

├── Google News: Star Wars
├── Reddit: r/StarWars
└── Reddit: r/StarWarsLeaks
```

The backend periodically fetches those feeds and stores their latest stories.

When the frontend requests stories for a topic, the API reads the already-stored stories from MongoDB rather than waiting for the external feeds to respond.

```text
External Feed
     ↓
   Pointer
     ↓
Background Refresh
     ↓
   MongoDB
     ↓
  FastAPI
     ↓
 Frontend
```

---

# Architecture

The core data model consists of four resources:

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

A **topic** is a user-defined collection of feeds.

Topics belong to individual users and allow each user to organize their feed however they want.

Example:

```json
{
  "_id": "...",
  "userId": "...",
  "topic": "Star Wars",
  "pointers": ["...", "..."]
}
```

Topics do not directly own stories.

Instead, they contain references to pointers, and stories belong to those pointers.

This keeps user organization separate from the underlying feed data.

---

## Pointers

A **pointer** represents a unique external feed.

Examples:

```text
https://www.reddit.com/r/StarWars.rss

https://www.reddit.com/r/MarvelStudiosSpoilers.rss

Google News RSS feeds
```

Pointers are shared resources.

If multiple users or topics follow the same external feed, they reference the same pointer instead of creating duplicate copies.

```text
User A Topic ──┐
               ├── Pointer ── Stories
User B Topic ──┘
```

This allows The Feed to follow a simple principle:

> **Fetch once, reuse many times.**

The backend only needs to request a shared external feed once regardless of how many topics use it.

Pointers also contain information used by the background refresh system:

```text
url
normalized_url
feed_type
last_fetched
next_fetch
created_at
updated_at
```

Before a pointer is created, its URL is normalized and checked against existing pointers.

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

The `source` identifies where the story originated, such as:

```text
reddit
google
```

`published_at` may be `null` when the source feed does not provide a publication timestamp.

Stories are stored in MongoDB rather than fetched whenever a user opens their feed.

---

# Feed Retrieval

When a user requests stories for a topic:

```text
Topic
  ↓
Pointer IDs
  ↓
Stories matching those pointers
  ↓
API Response
  ↓
Frontend
```

Conceptually, story retrieval uses the topic's pointer IDs:

```python
{
    "pointer_id": {
        "$in": topic.pointers
    }
}
```

Because the stories have already been collected by the background system, normal API requests do not need to make external RSS requests.

This helps keep feed retrieval fast and separates **reading stories** from **fetching stories**.

---

# Background Refresh System

External feed retrieval happens independently from normal API requests.

**APScheduler** periodically runs the story refresh process.

```text
APScheduler
     ↓
Find pointers ready for refresh
     ↓
Fetch RSS / Atom feed
     ↓
Parse stories
     ↓
Store latest stories
     ↓
Update pointer schedule
```

A pointer is ready to refresh when:

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

A delay is placed between external requests to reduce unnecessary traffic and lower the chance of hitting provider rate limits.

A failure while refreshing one pointer should not prevent the remaining pointers from being processed.

---

# Pointer Deduplication

Pointers are deduplicated globally using their normalized URL.

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
  └── ID ─┘
      ↓
Add pointer ID to topic
```

This prevents multiple copies of the same external source from being created.

Topic names are intentionally **not** globally deduplicated.

For example:

```text
Star Wars
Star Wars News
Star Wars Updates
Lucasfilm
```

may overlap, but users are free to organize their feeds however they want.

The important shared resource is the **pointer**, not the topic name.

---

# MongoDB Indexes

Indexes are created during FastAPI application startup.

Important indexes include:

### Unique Pointer URLs

```python
collection.create_index(
    "normalized_url",
    unique=True,
)
```

Prevents duplicate shared pointers.

### Pointer Refresh Scheduling

```python
collection.create_index("next_fetch")
```

Improves queries that find pointers ready to refresh.

### Stories by Pointer

```python
collection.create_index("pointer_id")
```

Improves story retrieval and deletion by pointer.

### Topics by User

```python
collection.create_index("userId")
```

Improves retrieval of a user's topics.

Where appropriate, database-level indexes enforce guarantees rather than relying only on application logic.

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

MongoDB `ObjectId` values cannot be returned directly as standard JSON.

The API therefore uses outbound models to convert MongoDB-specific values into JSON-friendly representations.

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
Internal Application Logic
   ↓
Outbound Model
   ↓
FastAPI
   ↓
JSON
   ↓
Frontend
```

This keeps database-specific types inside the backend while exposing clean API responses to clients.

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

The Feed currently supports:

- **Reddit RSS / Atom feeds**
- **Google News RSS feeds**

Each source is converted into the same common Story model so the frontend does not need to understand the differences between individual RSS providers.

---

# Design Goals

The Feed Backend is designed around a few core principles:

- **Give users control** — users decide which topics and sources belong in their feed.
- **Fetch once, reuse many times** — shared pointers prevent duplicate requests to external sources.
- **Keep user organization flexible** — users can name and organize topics however they want.
- **Separate fetching from reading** — users read stored stories instead of waiting for external RSS requests.
- **Respect external services** — scheduled refreshes and delays reduce unnecessary requests.
- **Enforce shared-resource uniqueness** — MongoDB indexes prevent duplicate pointers.
- **Keep API responses clean** — MongoDB-specific types remain internal while clients receive JSON-friendly models.

---

# Project Goal

The goal of The Feed is simple:

> **Give users a way to stay informed about the things they care about without needing a traditional social media feed.**

The backend makes that possible by collecting, organizing, storing, and serving the sources the user chooses.

**You choose the topics.
You choose the sources.
The Feed handles the rest.**
