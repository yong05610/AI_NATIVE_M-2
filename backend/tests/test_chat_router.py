from unittest.mock import Mock

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.core.exceptions import AppException, app_exception_handler
from app.models.conversation import ConversationResponse
from app.routers import chat as chat_router


@pytest.fixture
def client():
    application = FastAPI()
    application.add_exception_handler(AppException, app_exception_handler)
    application.include_router(chat_router.router)

    with TestClient(application) as test_client:
        yield test_client


def test_create_chat_returns_saved_conversation(client, monkeypatch):
    saved_response = ConversationResponse(
        id="conversation-1",
        message="최근 학습 흐름을 분석해줘",
        answer="최근 학습시간은 안정적인 흐름입니다.",
        created_at="2026-09-25T00:00:00Z",
    )
    create_chat_answer = Mock(return_value=saved_response)
    monkeypatch.setattr(chat_router, "create_chat_answer", create_chat_answer)

    response = client.post(
        "/api/chat",
        json={"message": "최근 학습 흐름을 분석해줘"},
    )

    assert response.status_code == 200
    assert response.json() == saved_response.model_dump()
    create_chat_answer.assert_called_once()
    payload = create_chat_answer.call_args.args[0]
    assert payload.message == "최근 학습 흐름을 분석해줘"


def test_create_chat_rejects_blank_message(client, monkeypatch):
    create_chat_answer = Mock()
    monkeypatch.setattr(chat_router, "create_chat_answer", create_chat_answer)

    response = client.post("/api/chat", json={"message": "   "})

    assert response.status_code == 422
    create_chat_answer.assert_not_called()


def test_create_chat_returns_service_error(client, monkeypatch):
    create_chat_answer = Mock(
        side_effect=AppException(
            status_code=503,
            detail="Failed to create chat answer.",
        )
    )
    monkeypatch.setattr(chat_router, "create_chat_answer", create_chat_answer)

    response = client.post(
        "/api/chat",
        json={"message": "최근 학습 흐름을 분석해줘"},
    )

    assert response.status_code == 503
    assert response.json() == {"detail": "Failed to create chat answer."}
    create_chat_answer.assert_called_once()
