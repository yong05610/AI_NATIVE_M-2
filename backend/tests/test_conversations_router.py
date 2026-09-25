from unittest.mock import Mock

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.core.exceptions import AppException, app_exception_handler
from app.models.conversation import ConversationResponse
from app.routers import conversations as conversations_router


@pytest.fixture
def client():
    application = FastAPI()
    application.add_exception_handler(AppException, app_exception_handler)
    application.include_router(conversations_router.router)

    with TestClient(application) as test_client:
        yield test_client


def test_create_conversation_returns_created_record(client, monkeypatch):
    created_record = ConversationResponse(
        id="conversation-1",
        message="오늘 공부 요약해줘",
        answer="오늘은 90분 공부했습니다.",
        created_at="2026-09-25T10:00:00Z",
    )
    create_conversation = Mock(return_value=created_record)
    monkeypatch.setattr(
        conversations_router,
        "create_conversation",
        create_conversation,
    )

    response = client.post(
        "/api/conversations",
        json={
            "message": "오늘 공부 요약해줘",
            "answer": "오늘은 90분 공부했습니다.",
        },
    )

    assert response.status_code == 200
    assert response.json() == created_record.model_dump()
    create_conversation.assert_called_once()
    payload = create_conversation.call_args.args[0]
    assert payload.message == "오늘 공부 요약해줘"
    assert payload.answer == "오늘은 90분 공부했습니다."


def test_get_conversations_returns_record_list(client, monkeypatch):
    records = [
        ConversationResponse(
            id="conversation-2",
            message="두 번째 질문",
            answer="두 번째 답변",
            created_at="2026-09-25T11:00:00Z",
        ),
        ConversationResponse(
            id="conversation-1",
            message="첫 번째 질문",
            answer="첫 번째 답변",
            created_at="2026-09-25T10:00:00Z",
        ),
    ]
    list_conversations = Mock(return_value=records)
    monkeypatch.setattr(
        conversations_router,
        "list_conversations",
        list_conversations,
    )

    response = client.get("/api/conversations")

    assert response.status_code == 200
    assert response.json() == [record.model_dump() for record in records]
    assert len(response.json()) == 2
    list_conversations.assert_called_once_with()


def test_get_conversation_returns_record(client, monkeypatch):
    record = ConversationResponse(
        id="conversation-1",
        message="질문",
        answer="답변",
        created_at="2026-09-25T10:00:00Z",
    )
    get_conversation = Mock(return_value=record)
    monkeypatch.setattr(
        conversations_router,
        "get_conversation",
        get_conversation,
    )

    response = client.get("/api/conversations/conversation-1")

    assert response.status_code == 200
    assert response.json() == record.model_dump()
    get_conversation.assert_called_once_with("conversation-1")


def test_get_conversation_returns_404_when_record_missing(client, monkeypatch):
    get_conversation = Mock(
        side_effect=AppException(
            status_code=404,
            detail="Conversation not found.",
        )
    )
    monkeypatch.setattr(
        conversations_router,
        "get_conversation",
        get_conversation,
    )

    response = client.get("/api/conversations/missing")

    assert response.status_code == 404
    assert response.json() == {"detail": "Conversation not found."}
    get_conversation.assert_called_once_with("missing")


def test_delete_conversation_returns_success_message(client, monkeypatch):
    delete_conversation = Mock()
    monkeypatch.setattr(
        conversations_router,
        "delete_conversation",
        delete_conversation,
    )

    response = client.delete("/api/conversations/conversation-1")

    assert response.status_code == 200
    assert response.json() == {"message": "Conversation deleted successfully"}
    delete_conversation.assert_called_once_with("conversation-1")


def test_delete_conversation_returns_404_when_record_missing(client, monkeypatch):
    delete_conversation = Mock(
        side_effect=AppException(
            status_code=404,
            detail="Conversation not found.",
        )
    )
    monkeypatch.setattr(
        conversations_router,
        "delete_conversation",
        delete_conversation,
    )

    response = client.delete("/api/conversations/missing")

    assert response.status_code == 404
    assert response.json() == {"detail": "Conversation not found."}
    delete_conversation.assert_called_once_with("missing")


def test_create_conversation_rejects_blank_message(client, monkeypatch):
    create_conversation = Mock()
    monkeypatch.setattr(
        conversations_router,
        "create_conversation",
        create_conversation,
    )

    response = client.post(
        "/api/conversations",
        json={"message": "   ", "answer": "답변"},
    )

    assert response.status_code == 422
    create_conversation.assert_not_called()


def test_get_conversations_returns_service_error(client, monkeypatch):
    list_conversations = Mock(
        side_effect=AppException(
            status_code=503,
            detail="Failed to list conversation.",
        )
    )
    monkeypatch.setattr(
        conversations_router,
        "list_conversations",
        list_conversations,
    )

    response = client.get("/api/conversations")

    assert response.status_code == 503
    assert response.json() == {"detail": "Failed to list conversation."}
    list_conversations.assert_called_once_with()
