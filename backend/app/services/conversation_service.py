"""AI 대화 기록의 Firestore 생성, 조회 및 삭제 서비스입니다."""

from datetime import datetime, timezone
from typing import Any

from app.core.exceptions import AppException
from app.models.conversation import ConversationInput, ConversationResponse
from app.services.firestore_service import get_conversations_collection


def _document_to_response(
    document_id: str,
    data: dict[str, Any],
) -> ConversationResponse:
    return ConversationResponse(
        id=document_id,
        message=data["message"],
        answer=data["answer"],
        created_at=data["created_at"],
    )


def _firestore_error(message: str) -> AppException:
    return AppException(status_code=503, detail=message)


def create_conversation(payload: ConversationInput) -> ConversationResponse:
    """질문과 답변 한 쌍을 새 대화 기록으로 저장합니다."""
    try:
        document = get_conversations_collection().document()
        data = {
            **payload.model_dump(),
            "created_at": datetime.now(timezone.utc)
            .isoformat()
            .replace("+00:00", "Z"),
        }
        document.set(data)
        return _document_to_response(document.id, data)
    except AppException:
        raise
    except Exception as exception:
        raise _firestore_error("Failed to create conversation.") from exception


def list_conversations() -> list[ConversationResponse]:
    """대화 기록을 생성 시각 내림차순으로 조회합니다."""
    try:
        records = [
            _document_to_response(snapshot.id, snapshot.to_dict() or {})
            for snapshot in get_conversations_collection().stream()
        ]
        return sorted(records, key=lambda record: record.created_at, reverse=True)
    except AppException:
        raise
    except Exception as exception:
        raise _firestore_error("Failed to list conversation.") from exception


def get_conversation(document_id: str) -> ConversationResponse:
    """문서 ID에 해당하는 대화 기록을 조회합니다."""
    try:
        snapshot = get_conversations_collection().document(document_id).get()
        if not snapshot.exists:
            raise AppException(status_code=404, detail="Conversation not found.")

        return _document_to_response(snapshot.id, snapshot.to_dict() or {})
    except AppException:
        raise
    except Exception as exception:
        raise _firestore_error("Failed to get conversation.") from exception


def delete_conversation(document_id: str) -> None:
    """문서 ID에 해당하는 대화 기록을 삭제합니다."""
    try:
        document = get_conversations_collection().document(document_id)
        if not document.get().exists:
            raise AppException(status_code=404, detail="Conversation not found.")

        document.delete()
    except AppException:
        raise
    except Exception as exception:
        raise _firestore_error("Failed to delete conversation.") from exception
