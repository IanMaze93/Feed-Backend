import os


def health_handler():
    return {
        "status": "ok",
        "service": "feed-backend",
        "env": os.getenv("APP_ENV", "local"),
    }
