from unittest.mock import MagicMock, patch

from src.database.update import (
    push_to_array,
    update_many,
    update_one,
    upsert_many,
    upsert_one,
)
from src.models.database.common import Collections


def test_update_one_calls_collection():
    mock_collection = MagicMock()
    query = {"_id": "123"}
    update = {"$set": {"name": "test"}}
    with patch("src.database.update.getCollection", return_value=mock_collection):
        update_one(Collections.TOPICS, query, update)
    mock_collection.update_one.assert_called_once_with(query, update)


def test_update_one_returns_result():
    mock_collection = MagicMock()
    mock_result = MagicMock()
    mock_collection.update_one.return_value = mock_result
    with patch("src.database.update.getCollection", return_value=mock_collection):
        result = update_one(Collections.TOPICS, {}, {})
    assert result is mock_result


def test_update_many_calls_collection():
    mock_collection = MagicMock()
    query = {"status": "inactive"}
    update = {"$set": {"status": "active"}}
    with patch("src.database.update.getCollection", return_value=mock_collection):
        update_many(Collections.TOPICS, query, update)
    mock_collection.update_many.assert_called_once_with(query, update)


def test_update_many_returns_result():
    mock_collection = MagicMock()
    mock_result = MagicMock()
    mock_collection.update_many.return_value = mock_result
    with patch("src.database.update.getCollection", return_value=mock_collection):
        result = update_many(Collections.TOPICS, {}, {})
    assert result is mock_result


def test_upsert_one_passes_upsert_flag():
    mock_collection = MagicMock()
    query = {"_id": "abc"}
    update = {"$set": {"x": 1}}
    with patch("src.database.update.getCollection", return_value=mock_collection):
        upsert_one(Collections.TOPICS, query, update)
    mock_collection.update_one.assert_called_once_with(query, update, upsert=True)


def test_upsert_many_passes_upsert_flag():
    mock_collection = MagicMock()
    query = {"type": "bot"}
    update = {"$set": {"active": True}}
    with patch("src.database.update.getCollection", return_value=mock_collection):
        upsert_many(Collections.TOPICS, query, update)
    mock_collection.update_many.assert_called_once_with(query, update, upsert=True)


def test_push_to_array_builds_push_update():
    mock_collection = MagicMock()
    query = {"_id": "user1"}
    with patch("src.database.update.getCollection", return_value=mock_collection):
        push_to_array(
            Collections.TOPICS,
            query,
            "messages",
            {"role": "user", "content": "hi"},
        )
    mock_collection.update_one.assert_called_once_with(
        query,
        {"$push": {"messages": {"role": "user", "content": "hi"}}},
    )
