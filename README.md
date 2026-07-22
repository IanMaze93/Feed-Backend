# Feed Backend

# Getting Started

## Install dependencies

```bash
poetry install
```

## Install Git hooks

```bash
poetry run pre-commit install
```

---

# Development

Run the API:

```bash
poetry run uvicorn src.main:app --reload
```

> Update the module path if the FastAPI application entry point changes.

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
