from unittest.mock import MagicMock

from src.database.update import (
    push_to_array,
    update_many,
    update_one,
    upsert_many,
    upsert_one,
)


def test_update_one_calls_collection():
    mock_collection = MagicMock()
    query = {"_id": "123"}
    update = {"$set": {"name": "test"}}
    update_one(mock_collection, query, update)
    mock_collection.update_one.assert_called_once_with(query, update)


def test_update_one_returns_result():
    mock_collection = MagicMock()
    mock_result = MagicMock()
    mock_collection.update_one.return_value = mock_result
    result = update_one(mock_collection, {}, {})
    assert result is mock_result


def test_update_many_calls_collection():
    mock_collection = MagicMock()
    query = {"status": "inactive"}
    update = {"$set": {"status": "active"}}
    update_many(mock_collection, query, update)
    mock_collection.update_many.assert_called_once_with(query, update)


def test_update_many_returns_result():
    mock_collection = MagicMock()
    mock_result = MagicMock()
    mock_collection.update_many.return_value = mock_result
    result = update_many(mock_collection, {}, {})
    assert result is mock_result


def test_upsert_one_passes_upsert_flag():
    mock_collection = MagicMock()
    query = {"_id": "abc"}
    update = {"$set": {"x": 1}}
    upsert_one(mock_collection, query, update)
    mock_collection.update_one.assert_called_once_with(query, update, upsert=True)


def test_upsert_many_passes_upsert_flag():
    mock_collection = MagicMock()
    query = {"type": "bot"}
    update = {"$set": {"active": True}}
    upsert_many(mock_collection, query, update)
    mock_collection.update_many.assert_called_once_with(query, update, upsert=True)


def test_push_to_array_builds_push_update():
    mock_collection = MagicMock()
    query = {"_id": "user1"}
    push_to_array(mock_collection, query, "messages", {"role": "user", "content": "hi"})
    mock_collection.update_one.assert_called_once_with(
        query,
        {"$push": {"messages": {"role": "user", "content": "hi"}}},
    )
