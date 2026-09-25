"""AI 채팅 API의 요청 모델입니다."""

from pydantic import BaseModel, field_validator


class ChatRequest(BaseModel):
    """AI 학습 코치에게 보내는 질문입니다."""

    message: str

    @field_validator("message")
    @classmethod
    def validate_not_blank(cls, value: str) -> str:
        """앞뒤 공백 제거 후 빈 문자열을 거부합니다."""
        stripped = value.strip()
        if not stripped:
            raise ValueError("message must not be blank")
        return stripped
