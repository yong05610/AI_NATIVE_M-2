from unittest.mock import Mock

import pytest

from app.core import firebase
from app.core.config import Settings
from app.core.exceptions import AppException


def _settings() -> Settings:
    return Settings(
        allowed_origins=(),
        firebase_project_id="test-project",
        firebase_client_email="firebase@test-project.iam.gserviceaccount.com",
        firebase_private_key="fake-private-key",
    )


def test_get_firebase_app_returns_existing_app(monkeypatch):
    existing_app = object()
    get_app = Mock(return_value=existing_app)
    certificate = Mock()
    initialize_app = Mock()
    get_settings = Mock()
    monkeypatch.setattr(firebase.firebase_admin, "get_app", get_app)
    monkeypatch.setattr(firebase.credentials, "Certificate", certificate)
    monkeypatch.setattr(firebase.firebase_admin, "initialize_app", initialize_app)
    monkeypatch.setattr(firebase, "get_settings", get_settings)

    result = firebase.get_firebase_app()

    get_app.assert_called_once_with()
    certificate.assert_not_called()
    initialize_app.assert_not_called()
    get_settings.assert_not_called()
    assert result is existing_app


def test_get_firebase_app_initializes_app_when_missing(monkeypatch):
    settings = _settings()
    credential = object()
    initialized_app = object()
    get_app = Mock(
        side_effect=[ValueError("not initialized"), ValueError("not initialized")]
    )
    certificate = Mock(return_value=credential)
    initialize_app = Mock(return_value=initialized_app)
    get_settings = Mock(return_value=settings)
    monkeypatch.setattr(firebase.firebase_admin, "get_app", get_app)
    monkeypatch.setattr(firebase.credentials, "Certificate", certificate)
    monkeypatch.setattr(firebase.firebase_admin, "initialize_app", initialize_app)
    monkeypatch.setattr(firebase, "get_settings", get_settings)

    result = firebase.get_firebase_app()

    assert get_app.call_count == 2
    get_settings.assert_called_once_with()
    certificate.assert_called_once_with(
        {
            "type": "service_account",
            "project_id": "test-project",
            "private_key": "fake-private-key",
            "client_email": "firebase@test-project.iam.gserviceaccount.com",
            "token_uri": "https://oauth2.googleapis.com/token",
        }
    )
    initialize_app.assert_called_once_with(
        credential,
        {"projectId": "test-project"},
    )
    assert result is initialized_app


def test_get_firebase_app_converts_certificate_error_to_503(monkeypatch):
    get_app = Mock(
        side_effect=[ValueError("not initialized"), ValueError("not initialized")]
    )
    certificate = Mock(side_effect=RuntimeError("invalid credential"))
    initialize_app = Mock()
    monkeypatch.setattr(firebase.firebase_admin, "get_app", get_app)
    monkeypatch.setattr(firebase.credentials, "Certificate", certificate)
    monkeypatch.setattr(firebase.firebase_admin, "initialize_app", initialize_app)
    monkeypatch.setattr(firebase, "get_settings", Mock(return_value=_settings()))

    with pytest.raises(AppException) as exception_info:
        firebase.get_firebase_app()

    assert exception_info.value.status_code == 503
    assert exception_info.value.detail == (
        "Firebase initialization failed. "
        "Check Firebase environment variables."
    )
    initialize_app.assert_not_called()


def test_get_firebase_app_converts_initialize_error_to_503(monkeypatch):
    credential = object()
    get_app = Mock(
        side_effect=[ValueError("not initialized"), ValueError("not initialized")]
    )
    certificate = Mock(return_value=credential)
    initialize_app = Mock(side_effect=RuntimeError("initialization failed"))
    monkeypatch.setattr(firebase.firebase_admin, "get_app", get_app)
    monkeypatch.setattr(firebase.credentials, "Certificate", certificate)
    monkeypatch.setattr(firebase.firebase_admin, "initialize_app", initialize_app)
    monkeypatch.setattr(firebase, "get_settings", Mock(return_value=_settings()))

    with pytest.raises(AppException) as exception_info:
        firebase.get_firebase_app()

    certificate.assert_called_once()
    initialize_app.assert_called_once_with(
        credential,
        {"projectId": "test-project"},
    )
    assert exception_info.value.status_code == 503
    assert exception_info.value.detail == (
        "Firebase initialization failed. "
        "Check Firebase environment variables."
    )


def test_get_firestore_client_uses_initialized_app(monkeypatch):
    initialized_app = object()
    firestore_client = object()
    get_app = Mock(return_value=initialized_app)
    create_client = Mock(return_value=firestore_client)
    monkeypatch.setattr(firebase, "get_firebase_app", get_app)
    monkeypatch.setattr(firebase.firestore, "client", create_client)

    result = firebase.get_firestore_client()

    get_app.assert_called_once_with()
    create_client.assert_called_once_with(app=initialized_app)
    assert result is firestore_client


def test_get_firestore_client_converts_client_error_to_503(monkeypatch):
    initialized_app = object()
    get_app = Mock(return_value=initialized_app)
    create_client = Mock(side_effect=RuntimeError("client creation failed"))
    monkeypatch.setattr(firebase, "get_firebase_app", get_app)
    monkeypatch.setattr(firebase.firestore, "client", create_client)

    with pytest.raises(AppException) as exception_info:
        firebase.get_firestore_client()

    get_app.assert_called_once_with()
    create_client.assert_called_once_with(app=initialized_app)
    assert exception_info.value.status_code == 503
    assert exception_info.value.detail == "Firestore client creation failed."
