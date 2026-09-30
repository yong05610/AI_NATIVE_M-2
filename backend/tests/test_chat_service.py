import json
from types import SimpleNamespace
from unittest.mock import Mock

import pytest
from pydantic import ValidationError

from app.core.exceptions import AppException
from app.models.chat import ChatRequest
from app.models.conversation import ConversationResponse
from app.services import chat_service


class Dumpable:
    def __init__(self, **data):
        self.data = data

    def model_dump(self):
        return self.data


def test_create_chat_answer_saves_conversation_once(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "  mock-api-key  ")
    monkeypatch.delenv("OPENAI_MODEL", raising=False)

    summary = Dumpable(count=12, total_minutes=660)
    records = [
        Dumpable(
            id=f"record-{index}",
            date=f"2026-09-{24 - index:02d}",
            value=60,
        )
        for index in range(12)
    ]
    mock_answer = "최근 학습시간은 안정적인 흐름입니다."
    completion = SimpleNamespace(
        choices=[SimpleNamespace(message=SimpleNamespace(content=mock_answer))]
    )
    completion_create = Mock(return_value=completion)
    client = SimpleNamespace(
        chat=SimpleNamespace(completions=SimpleNamespace(create=completion_create))
    )
    openai_constructor = Mock(return_value=client)
    saved_response = ConversationResponse(
        id="conversation-1",
        message="최근 학습 흐름을 분석해줘",
        answer=mock_answer,
        created_at="2026-09-25T00:00:00Z",
    )
    conversation_create = Mock(return_value=saved_response)
    summarize = Mock(return_value=summary)
    list_data = Mock(return_value=records)

    monkeypatch.setattr(chat_service, "summarize_study_data", summarize)
    monkeypatch.setattr(chat_service, "list_study_data", list_data)
    monkeypatch.setattr(chat_service, "OpenAI", openai_constructor)
    monkeypatch.setattr(chat_service, "create_conversation", conversation_create)

    result = chat_service.create_chat_answer(
        ChatRequest(message="최근 학습 흐름을 분석해줘")
    )

    summarize.assert_called_once_with()
    list_data.assert_called_once_with()
    openai_constructor.assert_called_once_with(api_key="mock-api-key")
    completion_create.assert_called_once()
    conversation_create.assert_called_once()

    openai_arguments = completion_create.call_args.kwargs
    assert openai_arguments["model"] == "gpt-4o-mini"
    user_content = openai_arguments["messages"][1]["content"]
    context_text = user_content.split("학습 데이터: ", 1)[1].split(
        "\n\n사용자 질문:",
        1,
    )[0]
    context = json.loads(context_text)
    assert len(context["recent_records"]) == 10
    assert context["recent_records"][0]["id"] == "record-0"
    assert context["recent_records"][-1]["id"] == "record-9"

    saved_payload = conversation_create.call_args.args[0]
    assert saved_payload.message == "최근 학습 흐름을 분석해줘"
    assert saved_payload.answer == mock_answer
    assert result == saved_response


def test_create_chat_answer_requires_api_key(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "   ")
    openai_constructor = Mock()
    summarize = Mock()
    list_data = Mock()
    conversation_create = Mock()

    monkeypatch.setattr(chat_service, "OpenAI", openai_constructor)
    monkeypatch.setattr(chat_service, "summarize_study_data", summarize)
    monkeypatch.setattr(chat_service, "list_study_data", list_data)
    monkeypatch.setattr(chat_service, "create_conversation", conversation_create)

    with pytest.raises(AppException) as exception_info:
        chat_service.create_chat_answer(ChatRequest(message="질문"))

    assert exception_info.value.status_code == 503
    assert exception_info.value.detail == "OpenAI API key is not configured."
    openai_constructor.assert_not_called()
    summarize.assert_not_called()
    list_data.assert_not_called()
    conversation_create.assert_not_called()


def test_create_chat_answer_logs_safe_openai_error(monkeypatch, caplog):
    api_key = "diagnostic-secret-key"
    monkeypatch.setenv("OPENAI_API_KEY", api_key)

    class AuthenticationError(Exception):
        status_code = 401
        code = "invalid_api_key"
        body = {
            "type": "invalid_request_error",
            "code": "invalid_api_key",
            "message": f"invalid key: {api_key}",
        }

    openai_error = AuthenticationError(f"authentication failed: {api_key}")
    completion_create = Mock(side_effect=openai_error)
    client = SimpleNamespace(
        chat=SimpleNamespace(completions=SimpleNamespace(create=completion_create))
    )
    conversation_create = Mock()

    monkeypatch.setattr(chat_service, "summarize_study_data", Mock(return_value=Dumpable()))
    monkeypatch.setattr(chat_service, "list_study_data", Mock(return_value=[]))
    monkeypatch.setattr(chat_service, "OpenAI", Mock(return_value=client))
    monkeypatch.setattr(chat_service, "create_conversation", conversation_create)

    with caplog.at_level("ERROR", logger=chat_service.__name__):
        with pytest.raises(AppException) as exception_info:
            chat_service.create_chat_answer(ChatRequest(message="질문"))

    assert exception_info.value.status_code == 503
    assert exception_info.value.detail == "OpenAI request failed: AuthenticationError"
    assert "exception_class=AuthenticationError" in caplog.text
    assert "status_code=401" in caplog.text
    assert "code=invalid_api_key" in caplog.text
    assert "[REDACTED]" in caplog.text
    assert api_key not in caplog.text
    conversation_create.assert_not_called()


def test_chat_request_rejects_blank_and_strips_whitespace():
    with pytest.raises(ValidationError):
        ChatRequest(message="   ")

    request = ChatRequest(message="  최근 학습 흐름을 분석해줘  ")
    assert request.message == "최근 학습 흐름을 분석해줘"
