import importlib
import sys
from unittest.mock import Mock

import dotenv
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.core import config
from app.core.config import Settings
from app.core.exceptions import AppException, app_exception_handler
from app.routers import health as health_router


@pytest.fixture
def client():
    application = FastAPI()
    application.add_exception_handler(AppException, app_exception_handler)
    application.include_router(health_router.router)

    with TestClient(application) as test_client:
        yield test_client


def test_root_health_returns_api_message(client):
    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {"message": "AI Study Time Assistant API"}


def test_firestore_health_returns_ok_without_external_access(client, monkeypatch):
    verify_connection = Mock()
    monkeypatch.setattr(
        health_router,
        "verify_firestore_connection",
        verify_connection,
    )

    response = client.get("/api/health/firestore")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "message": "Firestore connected",
    }
    verify_connection.assert_called_once_with()


def test_main_app_registers_root_health_endpoint(monkeypatch):
    load_dotenv = Mock(return_value=False)
    get_settings = Mock(
        return_value=Settings(
            allowed_origins=("http://localhost:5500",),
            firebase_project_id=None,
            firebase_client_email=None,
            firebase_private_key=None,
        )
    )
    verify_connection = Mock()
    monkeypatch.setattr(dotenv, "load_dotenv", load_dotenv)
    monkeypatch.setattr(config, "get_settings", get_settings)
    monkeypatch.setattr(
        health_router,
        "verify_firestore_connection",
        verify_connection,
    )
    monkeypatch.delitem(sys.modules, "main", raising=False)

    main = importlib.import_module("main")

    with TestClient(main.app) as test_client:
        response = test_client.get("/")

    assert response.status_code == 200
    assert response.json() == {"message": "AI Study Time Assistant API"}
    load_dotenv.assert_called_once()
    get_settings.assert_called_once_with()
    verify_connection.assert_not_called()


def test_openapi_includes_health_paths(client):
    response = client.get("/openapi.json")

    assert response.status_code == 200
    paths = response.json()["paths"]
    assert "get" in paths["/"]
    assert "get" in paths["/api/health/firestore"]
