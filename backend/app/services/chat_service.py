"""학습시간 데이터를 바탕으로 AI 답변을 생성하는 서비스입니다."""

import json
import logging
import os
import re
from typing import Any

from openai import OpenAI

from app.core.exceptions import AppException
from app.models.chat import ChatRequest
from app.models.conversation import ConversationInput, ConversationResponse
from app.services.conversation_service import create_conversation
from app.services.study_data_service import list_study_data, summarize_study_data


DEFAULT_OPENAI_MODEL = "gpt-4o-mini"
LOG_VALUE_LIMIT = 1000
SYSTEM_MESSAGE = (
    "당신은 학습시간 데이터를 분석해주는 친절한 한국어 AI 학습 코치입니다. "
    "제공된 학습 데이터를 근거로 사용자의 질문에 한국어로 답변하세요."
)
logger = logging.getLogger(__name__)


def _safe_log_value(value: Any, api_key: str) -> str | None:
    """로그 값에서 API 키 형태와 현재 키를 제거하고 길이를 제한합니다."""
    if value is None:
        return None

    text = value if isinstance(value, str) else repr(value)
    if api_key:
        text = text.replace(api_key, "[REDACTED]")
    text = re.sub(r"\bsk-[A-Za-z0-9_-]+\b", "[REDACTED]", text)
    text = re.sub(
        r"(?i)(authorization[\"']?\s*[:=]\s*[\"']?bearer\s+)[^\s\"']+",
        r"\1[REDACTED]",
        text,
    )
    return text[:LOG_VALUE_LIMIT]


def _safe_body_summary(body: Any, api_key: str) -> str | None:
    """OpenAI 오류 body에서 진단에 필요한 필드만 안전하게 요약합니다."""
    if isinstance(body, dict):
        summary = {
            key: body[key]
            for key in ("type", "code", "message", "param")
            if key in body
        }
        return _safe_log_value(summary, api_key)
    return _safe_log_value(body, api_key)


def _log_openai_exception(exception: Exception, api_key: str) -> None:
    """OpenAI 예외를 비밀값 없이 traceback과 함께 기록합니다."""
    body = getattr(exception, "body", None)
    code = getattr(exception, "code", None)
    if code is None and isinstance(body, dict):
        code = body.get("code")

    status_code = getattr(exception, "status_code", None)
    if status_code is None:
        status_code = getattr(exception, "status", None)

    message = getattr(exception, "message", None) or str(exception)
    safe_message = _safe_log_value(message, api_key)
    safe_traceback_exception = RuntimeError(
        f"{type(exception).__name__}: {safe_message}"
    )
    logger.exception(
        "OpenAI request failed: exception_class=%s repr=%s "
        "status_code=%s code=%s message=%s body=%s",
        type(exception).__name__,
        _safe_log_value(repr(exception), api_key),
        status_code,
        _safe_log_value(code, api_key),
        safe_message,
        _safe_body_summary(body, api_key),
        exc_info=(
            RuntimeError,
            safe_traceback_exception,
            exception.__traceback__,
        ),
    )


def _build_study_context() -> str:
    summary = summarize_study_data()
    recent_records = list_study_data()[:10]
    return json.dumps(
        {
            "summary": summary.model_dump(),
            "recent_records": [record.model_dump() for record in recent_records],
        },
        ensure_ascii=False,
    )


def create_chat_answer(payload: ChatRequest) -> ConversationResponse:
    """학습 데이터 기반 답변을 생성하고 대화 기록으로 저장합니다."""
    api_key = (os.getenv("OPENAI_API_KEY") or "").strip()
    if not api_key:
        raise AppException(
            status_code=503,
            detail="OpenAI API key is not configured.",
        )

    study_context = _build_study_context()
    model = os.getenv("OPENAI_MODEL") or DEFAULT_OPENAI_MODEL

    try:
        client = OpenAI(api_key=api_key)
        completion = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": SYSTEM_MESSAGE},
                {
                    "role": "user",
                    "content": (
                        f"학습 데이터: {study_context}\n\n"
                        f"사용자 질문: {payload.message}"
                    ),
                },
            ],
        )
        answer = completion.choices[0].message.content
        if not answer or not answer.strip():
            raise ValueError("OpenAI returned an empty answer.")
    except Exception as exception:
        _log_openai_exception(exception, api_key)
        raise AppException(
            status_code=503,
            detail=f"OpenAI request failed: {type(exception).__name__}",
        ) from exception

    return create_conversation(
        ConversationInput(message=payload.message, answer=answer)
    )
