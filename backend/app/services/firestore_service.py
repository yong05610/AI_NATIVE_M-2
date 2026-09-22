"""Firestore 컬렉션 접근과 연결 확인 서비스입니다."""

from typing import TYPE_CHECKING

from app.core.exceptions import AppException
from app.core.firebase import get_firestore_client

if TYPE_CHECKING:
    from google.cloud.firestore_v1 import Client
    from google.cloud.firestore_v1.base_collection import BaseCollectionReference


DATA_COLLECTION = "data"
CONVERSATIONS_COLLECTION = "conversations"


def get_data_collection(
    client: "Client | None" = None,
) -> "BaseCollectionReference":
    """학습시간 시계열 데이터 컬렉션 참조를 반환합니다."""
    firestore_client = client or get_firestore_client()
    return firestore_client.collection(DATA_COLLECTION)


def get_conversations_collection(
    client: "Client | None" = None,
) -> "BaseCollectionReference":
    """질문·답변 1쌍 문서를 저장하는 컬렉션 참조를 반환합니다.

    각 문서는 message, answer, created_at 필드를 사용하며 messages 배열 기반
    다중 턴 구조는 사용하지 않습니다.
    """
    firestore_client = client or get_firestore_client()
    return firestore_client.collection(CONVERSATIONS_COLLECTION)


def verify_firestore_connection() -> None:
    """data 컬렉션을 최대 한 건 조회해 Firestore 접근을 확인합니다."""
    try:
        client = get_firestore_client()
        list(get_data_collection(client).limit(1).stream())
    except AppException:
        raise
    except Exception as exception:
        raise AppException(
            status_code=503,
            detail=(
                "Firestore connection failed. "
                "Check Firebase credentials and network access."
            ),
        ) from exception
