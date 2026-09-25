"""학습시간 데이터를 바탕으로 AI 답변을 생성하는 서비스입니다."""

import json
import os

from openai import OpenAI

from app.core.exceptions import AppException
from app.models.chat import ChatRequest
from app.models.conversation import ConversationInput, ConversationResponse
from app.services.conversation_service import create_conversation
from app.services.study_data_service import list_study_data, summarize_study_data


DEFAULT_OPENAI_MODEL = "gpt-4o-mini"
SYSTEM_MESSAGE = (
    "당신은 학습시간 데이터를 분석해주는 친절한 한국어 AI 학습 코치입니다. "
    "제공된 학습 데이터를 근거로 사용자의 질문에 한국어로 답변하세요."
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
    api_key = os.getenv("OPENAI_API_KEY")
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
        raise AppException(
            status_code=503,
            detail="Failed to create chat answer.",
        ) from exception

    return create_conversation(
        ConversationInput(message=payload.message, answer=answer)
    )
