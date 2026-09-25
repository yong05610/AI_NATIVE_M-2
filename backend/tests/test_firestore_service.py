from unittest.mock import Mock

import pytest

from app.core.exceptions import AppException
from app.services import firestore_service


def test_get_data_collection_uses_provided_client(monkeypatch):
    collection_reference = object()
    client = Mock()
    client.collection.return_value = collection_reference
    get_client = Mock()
    monkeypatch.setattr(firestore_service, "get_firestore_client", get_client)

    result = firestore_service.get_data_collection(client=client)

    client.collection.assert_called_once_with("data")
    get_client.assert_not_called()
    assert result is collection_reference


def test_get_conversations_collection_uses_provided_client(monkeypatch):
    collection_reference = object()
    client = Mock()
    client.collection.return_value = collection_reference
    get_client = Mock()
    monkeypatch.setattr(firestore_service, "get_firestore_client", get_client)

    result = firestore_service.get_conversations_collection(client=client)

    client.collection.assert_called_once_with("conversations")
    get_client.assert_not_called()
    assert result is collection_reference


def test_get_data_collection_creates_client_when_missing(monkeypatch):
    collection_reference = object()
    client = Mock()
    client.collection.return_value = collection_reference
    get_client = Mock(return_value=client)
    monkeypatch.setattr(firestore_service, "get_firestore_client", get_client)

    result = firestore_service.get_data_collection()

    get_client.assert_called_once_with()
    client.collection.assert_called_once_with("data")
    assert result is collection_reference


def test_get_conversations_collection_creates_client_when_missing(monkeypatch):
    collection_reference = object()
    client = Mock()
    client.collection.return_value = collection_reference
    get_client = Mock(return_value=client)
    monkeypatch.setattr(firestore_service, "get_firestore_client", get_client)

    result = firestore_service.get_conversations_collection()

    get_client.assert_called_once_with()
    client.collection.assert_called_once_with("conversations")
    assert result is collection_reference


def test_verify_firestore_connection_runs_limited_query(monkeypatch):
    client = Mock()
    collection = Mock()
    limited_query = Mock()
    limited_query.stream.return_value = []
    collection.limit.return_value = limited_query
    get_client = Mock(return_value=client)
    get_data_collection = Mock(return_value=collection)
    monkeypatch.setattr(firestore_service, "get_firestore_client", get_client)
    monkeypatch.setattr(
        firestore_service,
        "get_data_collection",
        get_data_collection,
    )

    result = firestore_service.verify_firestore_connection()

    get_client.assert_called_once_with()
    get_data_collection.assert_called_once_with(client)
    collection.limit.assert_called_once_with(1)
    limited_query.stream.assert_called_once_with()
    assert result is None


def test_verify_firestore_connection_preserves_app_exception(monkeypatch):
    expected_exception = AppException(status_code=503, detail="custom error")
    monkeypatch.setattr(
        firestore_service,
        "get_firestore_client",
        Mock(side_effect=expected_exception),
    )

    with pytest.raises(AppException) as exception_info:
        firestore_service.verify_firestore_connection()

    assert exception_info.value is expected_exception
    assert exception_info.value.status_code == 503
    assert exception_info.value.detail == "custom error"


def test_verify_firestore_connection_converts_general_error_to_503(monkeypatch):
    client = Mock()
    collection = Mock()
    limited_query = Mock()
    limited_query.stream.side_effect = RuntimeError("Firestore unavailable")
    collection.limit.return_value = limited_query
    monkeypatch.setattr(
        firestore_service,
        "get_firestore_client",
        Mock(return_value=client),
    )
    monkeypatch.setattr(
        firestore_service,
        "get_data_collection",
        Mock(return_value=collection),
    )

    with pytest.raises(AppException) as exception_info:
        firestore_service.verify_firestore_connection()

    assert exception_info.value.status_code == 503
    assert exception_info.value.detail == (
        "Firestore connection failed. "
        "Check Firebase credentials and network access."
    )
