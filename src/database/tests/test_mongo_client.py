from unittest.mock import MagicMock, patch

import src.database.mongo_client as mongo_client
from src.models.database.common import DataBaseName


def setup_function():
    mongo_client.client = None
    mongo_client.database = None


@patch("src.database.mongo_client.MongoClient")
@patch("src.database.mongo_client.os.getenv", return_value="mongodb://localhost:27017")
def test_get_client_uses_env_uri(mock_getenv, mock_mongo_client):
    mongo_client.getClient()

    mock_getenv.assert_called_once_with("MONGO_URI")
    mock_mongo_client.assert_called_once_with("mongodb://localhost:27017")


@patch("src.database.mongo_client.MongoClient")
@patch("src.database.mongo_client.os.getenv", return_value="mongodb://localhost:27017")
def test_get_client_returns_client(mock_getenv, mock_mongo_client):
    mock_client = MagicMock()
    mock_mongo_client.return_value = mock_client

    result = mongo_client.getClient()

    assert result is mock_client


@patch("src.database.mongo_client.MongoClient")
@patch("src.database.mongo_client.os.getenv", return_value="mongodb://localhost:27017")
def test_connect_to_database_returns_database(mock_getenv, mock_mongo_client):
    mock_client = MagicMock()
    mock_database = MagicMock()

    mock_client.__getitem__.return_value = mock_database
    mock_mongo_client.return_value = mock_client

    result = mongo_client.connectToDatabase()

    mock_client.__getitem__.assert_called_once_with(DataBaseName.EIGHT_BIT.value)
    assert result is mock_database
