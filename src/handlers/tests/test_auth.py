from datetime import datetime, timezone
from unittest.mock import patch

from bson import ObjectId

from src.handlers.auth import login_handler
from src.models.api.user import LoginPayload


def user_record(password_hash="hashed-password"):
    now = datetime.now(timezone.utc)
    return {
        "_id": ObjectId(),
        "firstName": "Ada",
        "lastName": "Lovelace",
        "email": "ada@example.com",
        "username": "ada",
        "passwordHash": password_hash,
        "createdAt": now,
        "updatedAt": now,
    }


def test_login_handler_returns_user_id_for_valid_credentials():
    record = user_record()
    payload = LoginPayload(username="ada", password="correct-password")

    with (
        patch("src.handlers.auth.find_one", return_value=record) as find_one,
        patch("src.handlers.auth.verify_password", return_value=True) as verify,
    ):
        result = login_handler(payload)

    assert result == str(record["_id"])
    find_one.assert_called_once()
    verify.assert_called_once_with("correct-password", "hashed-password")


def test_login_handler_returns_none_when_user_does_not_exist():
    payload = LoginPayload(username="missing", password="password")

    with patch("src.handlers.auth.find_one", return_value=None):
        assert login_handler(payload) is None


def test_login_handler_returns_none_for_invalid_password():
    payload = LoginPayload(username="ada", password="wrong-password")

    with (
        patch("src.handlers.auth.find_one", return_value=user_record()),
        patch("src.handlers.auth.verify_password", return_value=False),
    ):
        assert login_handler(payload) is None


def test_login_handler_wraps_database_errors():
    payload = LoginPayload(username="ada", password="password")

    with patch(
        "src.handlers.auth.find_one",
        side_effect=RuntimeError("database unavailable"),
    ):
        try:
            login_handler(payload)
        except ValueError as error:
            assert str(error) == "Error logging in user: database unavailable"
        else:
            raise AssertionError("login_handler did not raise ValueError")
