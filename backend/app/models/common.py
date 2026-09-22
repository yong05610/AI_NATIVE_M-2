"""API에서 공통으로 사용하는 응답 모델입니다."""

from pydantic import BaseModel


class MessageResponse(BaseModel):
    """단일 메시지 성공 응답입니다."""

    message: str


class ErrorResponse(BaseModel):
    """공통 오류 응답입니다."""

    detail: str


class HealthResponse(BaseModel):
    """외부 서비스 연결 상태 응답입니다."""

    status: str
    message: str
