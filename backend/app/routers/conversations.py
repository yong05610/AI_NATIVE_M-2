"""AI 대화 기록 생성, 조회 및 삭제 API 라우터입니다."""

from fastapi import APIRouter

from app.models.common import ErrorResponse, MessageResponse
from app.models.conversation import ConversationInput, ConversationResponse
from app.services.conversation_service import (
    create_conversation,
    delete_conversation,
    get_conversation,
    list_conversations,
)


router = APIRouter(prefix="/api/conversations", tags=["conversations"])


@router.post(
    "",
    response_model=ConversationResponse,
    responses={503: {"model": ErrorResponse}},
)
def create_conversation_record(
    payload: ConversationInput,
) -> ConversationResponse:
    return create_conversation(payload)


@router.get(
    "",
    response_model=list[ConversationResponse],
    responses={503: {"model": ErrorResponse}},
)
def get_conversations() -> list[ConversationResponse]:
    return list_conversations()


@router.get(
    "/{document_id}",
    response_model=ConversationResponse,
    responses={404: {"model": ErrorResponse}, 503: {"model": ErrorResponse}},
)
def get_conversation_record(document_id: str) -> ConversationResponse:
    return get_conversation(document_id)


@router.delete(
    "/{document_id}",
    response_model=MessageResponse,
    responses={404: {"model": ErrorResponse}, 503: {"model": ErrorResponse}},
)
def delete_conversation_record(document_id: str) -> MessageResponse:
    delete_conversation(document_id)
    return MessageResponse(message="Conversation deleted successfully")
