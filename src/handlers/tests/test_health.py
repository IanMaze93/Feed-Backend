from src.handlers.health import health_handler
from src.handlers.root import root_handler


def test_health_handler_returns_service_status(monkeypatch):
    monkeypatch.setenv("APP_ENV", "test")

    assert health_handler() == {
        "status": "ok",
        "service": "feed-backend",
        "env": "test",
    }


def test_health_handler_defaults_to_local_environment(monkeypatch):
    monkeypatch.delenv("APP_ENV", raising=False)

    assert health_handler()["env"] == "local"


def test_root_handler_returns_welcome_message_and_docs_path():
    assert root_handler() == {
        "message": "Welcome to the Feed Backend API",
        "docs": "/docs",
    }
