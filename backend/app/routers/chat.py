"""AI 학습 코치 채팅 API 라우터입니다."""

from fastapi import APIRouter

from app.models.chat import ChatRequest
from app.models.common import ErrorResponse
from app.models.conversation import ConversationResponse
from app.services.chat_service import create_chat_answer


router = APIRouter(prefix="/api/chat", tags=["chat"])


@router.post(
    "",
    response_model=ConversationResponse,
    responses={503: {"model": ErrorResponse}},
)
def create_chat(payload: ChatRequest) -> ConversationResponse:
    return create_chat_answer(payload)
