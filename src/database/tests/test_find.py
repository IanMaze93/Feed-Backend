from unittest.mock import MagicMock, patch

from src.database.find import find_many, find_one
from src.models.database.common import Collections


def test_find_one_calls_collection_find_one():
    mock_collection = MagicMock()
    query = {"_id": "123"}
    with patch(
        "src.database.find.getCollection", return_value=mock_collection
    ) as mock_get_collection:
        find_one(Collections.TOPICS, query)

    mock_get_collection.assert_called_once_with(Collections.TOPICS)
    mock_collection.find_one.assert_called_once_with(query)


def test_find_one_returns_result():
    mock_collection = MagicMock()
    mock_collection.find_one.return_value = {"_id": "123", "name": "test"}
    with patch("src.database.find.getCollection", return_value=mock_collection):
        result = find_one(Collections.TOPICS, {"_id": "123"})

    assert result == {"_id": "123", "name": "test"}


def test_find_one_returns_none_when_not_found():
    mock_collection = MagicMock()
    mock_collection.find_one.return_value = None
    with patch("src.database.find.getCollection", return_value=mock_collection):
        result = find_one(Collections.TOPICS, {"_id": "missing"})

    assert result is None


def test_find_many_calls_collection_find():
    mock_collection = MagicMock()
    query = {"status": "active"}
    with patch(
        "src.database.find.getCollection", return_value=mock_collection
    ) as mock_get_collection:
        find_many(Collections.TOPICS, query)

    mock_get_collection.assert_called_once_with(Collections.TOPICS)
    mock_collection.find.assert_called_once_with(query)


def test_find_many_returns_cursor():
    mock_collection = MagicMock()
    mock_cursor = MagicMock()
    mock_collection.find.return_value = mock_cursor
    with patch("src.database.find.getCollection", return_value=mock_collection):
        result = find_many(Collections.TOPICS, {"status": "active"})

    assert result is mock_cursor
