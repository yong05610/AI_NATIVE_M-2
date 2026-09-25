"""AI 대화 기록 API의 요청 및 응답 모델입니다."""

from pydantic import BaseModel, field_validator


class ConversationInput(BaseModel):
    """대화 기록 생성 요청입니다."""

    message: str
    answer: str

    @field_validator("message", "answer")
    @classmethod
    def validate_not_blank(cls, value: str) -> str:
        """앞뒤 공백 제거 후 빈 문자열을 거부합니다."""
        stripped = value.strip()
        if not stripped:
            raise ValueError("field must not be blank")
        return stripped


class ConversationResponse(BaseModel):
    """대화 기록 문서 응답입니다."""

    id: str
    message: str
    answer: str
    created_at: str
