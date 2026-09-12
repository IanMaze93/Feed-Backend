import os
from datetime import datetime, timedelta, timezone

import jwt
import pytest
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials

os.environ.setdefault("JWT_SECRET", "test-secret")

from src.tools.auth.token import (  # noqa: E402
    ALGORITHM,
    SECRET_KEY,
    create_access_token,
    get_current_user_id,
    validate_user_id,
)


def credentials_for(token: str) -> HTTPAuthorizationCredentials:
    return HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)


def test_create_access_token_contains_user_and_expiration():
    token = create_access_token("user-123")

    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

    assert payload["sub"] == "user-123"
    assert payload["exp"] > datetime.now(timezone.utc).timestamp()


def test_get_current_user_id_returns_subject_from_valid_token():
    token = create_access_token("user-123")

    assert get_current_user_id(credentials_for(token)) == "user-123"


def test_get_current_user_id_rejects_expired_token():
    token = jwt.encode(
        {
            "sub": "user-123",
            "exp": datetime.now(timezone.utc) - timedelta(minutes=1),
        },
        SECRET_KEY,
        algorithm=ALGORITHM,
    )

    with pytest.raises(HTTPException) as error:
        get_current_user_id(credentials_for(token))

    assert error.value.status_code == 401
    assert error.value.detail == "Invalid or expired token"


def test_get_current_user_id_rejects_token_without_subject():
    token = jwt.encode(
        {"exp": datetime.now(timezone.utc) + timedelta(minutes=1)},
        SECRET_KEY,
        algorithm=ALGORITHM,
    )

    with pytest.raises(HTTPException) as error:
        get_current_user_id(credentials_for(token))

    assert error.value.status_code == 401
    assert error.value.detail == "Invalid authentication credentials"


def test_get_current_user_id_rejects_malformed_token():
    with pytest.raises(HTTPException) as error:
        get_current_user_id(credentials_for("not-a-token"))

    assert error.value.status_code == 401
    assert error.value.detail == "Invalid or expired token"


@pytest.mark.parametrize(
    ("user_id", "token_user_id", "expected"),
    [("user-123", "user-123", True), ("user-123", "user-456", False)],
)
def test_validate_user_id(user_id, token_user_id, expected):
    assert validate_user_id(user_id, token_user_id) is expected
