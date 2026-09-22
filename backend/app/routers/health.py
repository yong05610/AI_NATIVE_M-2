"""기본 서버 상태 확인 라우터입니다."""

from fastapi import APIRouter

from app.models.common import ErrorResponse, HealthResponse, MessageResponse
from app.services.firestore_service import verify_firestore_connection


router = APIRouter(tags=["health"])


@router.get("/", response_model=MessageResponse)
async def read_root() -> MessageResponse:
    """서버가 요청을 처리할 수 있는지 확인합니다."""
    return MessageResponse(message="AI Study Time Assistant API")


@router.get(
    "/api/health/firestore",
    response_model=HealthResponse,
    responses={503: {"model": ErrorResponse}},
)
def read_firestore_health() -> HealthResponse:
    """제한 조회를 실행해 Firestore 연결 상태를 확인합니다."""
    verify_firestore_connection()
    return HealthResponse(status="ok", message="Firestore connected")
