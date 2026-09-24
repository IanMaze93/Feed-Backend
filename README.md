# The Feed - Backend

<img src="./src/images/logo-feed.png">

**Your news. Your topics. No socials.**

The Feed Backend is the API and feed-processing service behind **The Feed**, a personalized news aggregator designed to give users more control over the content they see.

Instead of relying on a traditional social media feed filled with advertisements, promoted content, and algorithmic recommendations, The Feed allows users to define the topics and sources they want to follow.

Users create **topics** and attach **pointers** to external sources such as Reddit or Google News. The backend retrieves stories from those sources, stores them in MongoDB, and makes them available to The Feed frontend through the API.

### Live Application

**https://feed.mazeian.dev**

## Tech Stack

The backend is built with:

- **Python 3.12+**
- **FastAPI**
- **MongoDB**
- **PyMongo**
- **Pydantic**
- **APScheduler**
- **Feedparser**
- **PyJWT**
- **Argon2**
- **Poetry**
- **Docker**
- **Pytest**
- **Ruff**
- **GitHub Actions**

Currently supported feed sources include:

- **Google News**
- **Reddit**
- **Standard RSS feeds**

Additional source types can be added as the project grows.

---

# Features

The Feed Backend currently provides:

- User account creation
- Secure password hashing with Argon2
- JWT-based authentication
- Bearer-token protected API routes
- User-owned topics
- Shared external feed pointers
- Global pointer deduplication
- Reddit RSS/Atom ingestion
- Google News RSS ingestion
- Scheduled background feed refreshes
- Persistent story storage in MongoDB
- Per-user and per-topic story retrieval
- MongoDB indexes for common queries and uniqueness constraints
- Automatic FastAPI/OpenAPI documentation
- Docker-based deployment
- GitHub Actions CI for linting, formatting, and tests

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
├── Reddit: r/StarWarsLeaks
└── RSS: StarWars.com
```

The backend periodically fetches those feeds and stores their latest stories.

When the frontend requests stories for a topic, the API reads the already-stored stories from MongoDB rather than waiting for external feeds to respond.

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

This separates **collecting stories** from **reading stories**, keeping normal feed requests fast and reducing unnecessary traffic to external providers.

---

# Authentication

The Feed uses username/password authentication with JWT bearer tokens.

Passwords are never stored directly.

During account creation:

```text
Password
   ↓
Argon2 Hash
   ↓
MongoDB
```

During login:

```text
Username + Password
        ↓
Verify Password Hash
        ↓
Create JWT Access Token
        ↓
Return Bearer Token
```

The login endpoint returns:

```json
{
  "access_token": "...",
  "token_type": "bearer",
  "user_id": "..."
}
```

Access tokens currently expire after **60 minutes**.

Protected requests use the standard HTTP authorization header:

```http
Authorization: Bearer <access_token>
```

For user-specific routes, the backend verifies that the user ID contained in the token matches the user ID requested in the URL.

Conceptually:

```text
Request
   ↓
Bearer Token
   ↓
Validate JWT
   ↓
Extract User ID
   ↓
Compare Against Requested User
   ↓
Protected Resource
```

An authenticated user cannot access another user's protected resources simply by changing the user ID in the request URL.

JWT signing uses the server-side `JWT_SECRET` environment variable.

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

The separation between user organization and external feed data is intentional.

Topics belong to users.

Pointers represent shared external resources.

Stories belong to pointers.

This allows multiple users to follow the same source without The Feed repeatedly fetching identical external data.

---

## Users

A user represents an account within The Feed.

Users contain authentication information along with their application identity.

Passwords are stored as Argon2 hashes rather than plaintext.

User-specific API routes require a valid JWT belonging to that user.

---

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
Authenticated User
       ↓
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

The backend can also combine stories across all of a user's topics to construct their complete feed.

---

# Background Refresh System

External feed retrieval happens independently from normal API requests.

**APScheduler** runs the story refresh process in the background.

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

Because refreshing occurs independently from normal feed retrieval, users do not need to wait for external RSS providers when loading their feeds.

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

For example, if several users follow:

```text
r/StarWars
```

The Feed does not need to maintain a separate Reddit pointer and set of stories for every user.

Instead:

```text
User A ──┐
User B ──┼── Shared Pointer ── Stories
User C ──┘
```

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

# API Overview

FastAPI automatically exposes interactive API documentation while the backend is running.

```text
/docs
```

The root endpoint also provides a link to the generated documentation.

## Health

```http
GET /health
```

Returns the current health of the backend service.

---

## Authentication

### Login

```http
POST /auth/login
```

Authenticates an existing user and returns a JWT bearer token.

---

## Users

### Create User

```http
POST /users
```

Creates a new user account.

### Get User

```http
GET /users/{user_id}
```

Requires authentication for the requested user.

---

## Topics

### Create Topic

```http
POST /users/{user_id}/topics
```

Creates a topic belonging to the authenticated user.

### Update Topics

```http
PUT /users/{user_id}/topics
```

Updates the authenticated user's topics.

### Get Topics

```http
GET /users/{user_id}/topics
```

Returns the authenticated user's topics.

### Delete Topic

```http
POST /users/{user_id}/topics/{topic_id}/delete
```

Deletes a topic.

---

## Pointers

### Add Pointer to Topic

```http
POST /users/{user_id}/topics/{topic_id}/pointers
```

Adds an external feed pointer to a topic.

### Get Pointer

```http
GET /users/{user_id}/pointers/{pointer_id}
```

Returns information about a pointer.

### Delete Pointer

```http
POST /users/{user_id}/pointers/{pointer_id}/delete
```

Deletes a pointer.

---

## Stories

### Get Stories by Topic

```http
GET /users/{user_id}/topics/{topic_id}/stories
```

Returns stories associated with the pointers attached to a specific topic.

### Get All Stories for User

```http
GET /users/{user_id}/stories
```

Returns stories across the authenticated user's topics.

---

# Environment Variables

The backend requires the following environment variables:

```env
MONGO_URI=
APP_ENV=
JWT_SECRET=
```

An example configuration is provided in:

```text
.env.example
```

Copy the example file when creating a local environment:

```bash
cp .env.example .env
```

Then replace the example values with your own development configuration.

### `MONGO_URI`

Connection URI used to connect to MongoDB.

### `APP_ENV`

Identifies the current application environment.

Example:

```env
APP_ENV=development
```

### `JWT_SECRET`

Secret used to sign and validate authentication tokens.

Use a strong randomly generated value outside of local testing.

The actual `.env` file is excluded from Git and should never be committed.

---

# Getting Started

## Requirements

The project requires:

- Python 3.12+
- Poetry
- MongoDB

Docker can also be used to run the configured services.

---

## Clone the Repository

```bash
git clone <repository-url>
cd Feed-Backend
```

---

## Install Dependencies

```bash
poetry install
```

---

## Configure Environment Variables

```bash
cp .env.example .env
```

Update the values in `.env` for your environment.

---

## Install Git Hooks

```bash
poetry run pre-commit install
```

---

# Development

Run the API locally:

```bash
poetry run uvicorn src.main:app --reload
```

FastAPI will expose interactive API documentation at:

```text
http://localhost:8000/docs
```

Run linting:

```bash
poetry run ruff check .
```

Format the project:

```bash
poetry run ruff format .
```

Check formatting without modifying files:

```bash
poetry run ruff format --check .
```

Run all pre-commit hooks:

```bash
poetry run pre-commit run --all-files
```

---

# Testing

The project uses **pytest**.

Run the test suite with:

```bash
poetry run pytest
```

Or use quiet output:

```bash
poetry run pytest -q
```

Testing infrastructure is configured, with automated test coverage being expanded as the project continues to develop.

Important areas for test coverage include:

- Authentication and invalid login attempts
- JWT validation
- User authorization
- Topic creation and updates
- Pointer URL normalization
- Pointer deduplication
- Story retrieval
- Background refresh behavior
- Invalid or missing resources

---

# Continuous Integration

The repository includes a **GitHub Actions** CI workflow.

CI runs automatically on pushes and pull requests targeting `main`.

The workflow currently:

```text
Checkout repository
      ↓
Install Python 3.12
      ↓
Install Poetry
      ↓
Install dependencies
      ↓
Validate Poetry configuration
      ↓
Ruff lint check
      ↓
Ruff format check
      ↓
Pytest
```

This helps catch linting, formatting, dependency, and test failures before changes are merged.

---

# Docker

Start all configured services:

```bash
docker compose up --build
```

Run them in the background:

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

Each provider is converted into the same common Story model.

```text
Reddit ──────┐
             │
Google News ─┼── Story Model ── MongoDB ── API ── Frontend
             │
Future Feed ─┘
```

This means the frontend does not need to understand the differences between individual RSS providers.

Additional providers can be added to the backend while continuing to expose the same general story structure to clients.

---

# Design Goals

The Feed Backend is designed around a few core principles:

- **Give users control** — users decide which topics and sources belong in their feed.

- **Fetch once, reuse many times** — shared pointers prevent duplicate requests to external sources.

- **Keep user data private** — authenticated routes verify that users only access resources belonging to their account.

- **Never store plaintext passwords** — credentials are protected using Argon2 password hashing.

- **Keep user organization flexible** — users can name and organize topics however they want.

- **Separate fetching from reading** — users read stored stories instead of waiting for external RSS requests.

- **Respect external services** — scheduled refreshes and delays reduce unnecessary requests.

- **Enforce shared-resource uniqueness** — MongoDB indexes prevent duplicate pointers.

- **Keep API responses clean** — MongoDB-specific types remain internal while clients receive JSON-friendly models.

- **Keep source integrations interchangeable** — different feed providers are converted into the same story representation.

---

# Project Goal

The goal of The Feed is simple:

> **Give users a way to stay informed about the things they care about without needing a traditional social media feed.**

The Feed is built around user-selected sources rather than algorithmically selected content.

The backend makes that possible by authenticating users, collecting their chosen sources, sharing common feed resources when possible, refreshing stories in the background, storing those stories, and serving them through a protected API.

**You choose the topics.**

**You choose the sources.**

**The Feed handles the rest.**
