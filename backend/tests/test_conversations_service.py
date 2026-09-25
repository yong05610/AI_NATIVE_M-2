from datetime import datetime
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from app.core.exceptions import AppException
from app.models.conversation import ConversationInput
from app.services import conversation_service


def test_create_conversation_writes_document_and_returns_response(monkeypatch):
    document = Mock()
    document.id = "conversation-1"
    collection = Mock()
    collection.document.return_value = document
    get_collection = Mock(return_value=collection)
    monkeypatch.setattr(
        conversation_service,
        "get_conversations_collection",
        get_collection,
    )
    payload = ConversationInput(
        message="최근 학습 흐름을 알려줘",
        answer="최근 학습시간은 증가하고 있습니다.",
    )

    result = conversation_service.create_conversation(payload)

    get_collection.assert_called_once_with()
    collection.document.assert_called_once_with()
    document.set.assert_called_once()
    saved_data = document.set.call_args.args[0]
    assert saved_data["message"] == payload.message
    assert saved_data["answer"] == payload.answer
    assert saved_data["created_at"].endswith("Z")
    datetime.fromisoformat(saved_data["created_at"].replace("Z", "+00:00"))
    assert result.id == "conversation-1"
    assert result.message == payload.message
    assert result.answer == payload.answer
    assert result.created_at == saved_data["created_at"]


def test_list_conversations_converts_and_sorts_documents(monkeypatch):
    snapshots = [
        SimpleNamespace(
            id="older",
            to_dict=Mock(
                return_value={
                    "message": "이전 질문",
                    "answer": "이전 답변",
                    "created_at": "2026-09-24T10:00:00Z",
                }
            ),
        ),
        SimpleNamespace(
            id="newer",
            to_dict=Mock(
                return_value={
                    "message": "최근 질문",
                    "answer": "최근 답변",
                    "created_at": "2026-09-25T10:00:00Z",
                }
            ),
        ),
    ]
    collection = Mock()
    collection.stream.return_value = snapshots
    monkeypatch.setattr(
        conversation_service,
        "get_conversations_collection",
        Mock(return_value=collection),
    )

    records = conversation_service.list_conversations()

    collection.stream.assert_called_once_with()
    assert len(records) == 2
    assert [record.id for record in records] == ["newer", "older"]
    assert records[0].message == "최근 질문"
    assert records[0].answer == "최근 답변"
    assert records[0].created_at == "2026-09-25T10:00:00Z"


def test_get_conversation_returns_existing_document(monkeypatch):
    snapshot = SimpleNamespace(
        id="conversation-1",
        exists=True,
        to_dict=Mock(
            return_value={
                "message": "질문",
                "answer": "답변",
                "created_at": "2026-09-25T10:00:00Z",
            }
        ),
    )
    document = Mock()
    document.get.return_value = snapshot
    collection = Mock()
    collection.document.return_value = document
    monkeypatch.setattr(
        conversation_service,
        "get_conversations_collection",
        Mock(return_value=collection),
    )

    result = conversation_service.get_conversation("conversation-1")

    collection.document.assert_called_once_with("conversation-1")
    document.get.assert_called_once_with()
    assert result.id == "conversation-1"
    assert result.message == "질문"
    assert result.answer == "답변"
    assert result.created_at == "2026-09-25T10:00:00Z"


def test_get_conversation_returns_404_when_document_missing(monkeypatch):
    document = Mock()
    document.get.return_value = SimpleNamespace(exists=False)
    collection = Mock()
    collection.document.return_value = document
    monkeypatch.setattr(
        conversation_service,
        "get_conversations_collection",
        Mock(return_value=collection),
    )

    with pytest.raises(AppException) as exception_info:
        conversation_service.get_conversation("missing")

    assert exception_info.value.status_code == 404
    assert exception_info.value.detail == "Conversation not found."


def test_delete_conversation_deletes_existing_document(monkeypatch):
    document = Mock()
    document.get.return_value = SimpleNamespace(exists=True)
    collection = Mock()
    collection.document.return_value = document
    monkeypatch.setattr(
        conversation_service,
        "get_conversations_collection",
        Mock(return_value=collection),
    )

    result = conversation_service.delete_conversation("conversation-1")

    collection.document.assert_called_once_with("conversation-1")
    document.delete.assert_called_once_with()
    assert result is None


def test_delete_conversation_returns_404_when_document_missing(monkeypatch):
    document = Mock()
    document.get.return_value = SimpleNamespace(exists=False)
    collection = Mock()
    collection.document.return_value = document
    monkeypatch.setattr(
        conversation_service,
        "get_conversations_collection",
        Mock(return_value=collection),
    )

    with pytest.raises(AppException) as exception_info:
        conversation_service.delete_conversation("missing")

    assert exception_info.value.status_code == 404
    assert exception_info.value.detail == "Conversation not found."
    document.delete.assert_not_called()


def test_list_conversations_converts_firestore_error_to_503(monkeypatch):
    monkeypatch.setattr(
        conversation_service,
        "get_conversations_collection",
        Mock(side_effect=RuntimeError("Firestore unavailable")),
    )

    with pytest.raises(AppException) as exception_info:
        conversation_service.list_conversations()

    assert exception_info.value.status_code == 503
    assert exception_info.value.detail == "Failed to list conversation."
