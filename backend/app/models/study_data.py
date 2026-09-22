"""학습시간 데이터 API의 요청 및 응답 모델입니다."""

from datetime import date as date_type
from typing import Literal

from pydantic import BaseModel, Field, field_validator


class StudyDataInput(BaseModel):
    """학습시간 생성 및 수정 요청입니다."""

    date: str
    value: float = Field(gt=0, allow_inf_nan=False)
    memo: str = ""

    @field_validator("date")
    @classmethod
    def validate_date(cls, value: str) -> str:
        """날짜가 정확한 YYYY-MM-DD 형식인지 검증합니다."""
        try:
            parsed_date = date_type.fromisoformat(value)
        except ValueError as exception:
            raise ValueError("date must use YYYY-MM-DD format") from exception

        if parsed_date.isoformat() != value:
            raise ValueError("date must use YYYY-MM-DD format")
        return value


class StudyDataResponse(BaseModel):
    """학습시간 문서 응답입니다."""

    id: str
    date: str
    value: float
    memo: str


class StudyDataSummaryResponse(BaseModel):
    """학습시간 데이터 요약 응답입니다."""

    count: int
    total_minutes: float
    average_minutes: float
    max_minutes: float
    min_minutes: float
    recent_7_days_total: float
    recent_trend: Literal[
        "increasing",
        "decreasing",
        "stable",
        "not_enough_data",
    ]
