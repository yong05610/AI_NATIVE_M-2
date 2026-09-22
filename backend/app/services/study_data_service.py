"""학습시간 데이터의 Firestore CRUD 및 요약 계산 서비스입니다."""

from datetime import date, datetime, timedelta
from typing import Any

from firebase_admin import firestore

from app.core.exceptions import AppException
from app.models.study_data import (
    StudyDataInput,
    StudyDataResponse,
    StudyDataSummaryResponse,
)
from app.services.firestore_service import get_data_collection


def _document_to_response(document_id: str, data: dict[str, Any]) -> StudyDataResponse:
    return StudyDataResponse(
        id=document_id,
        date=data["date"],
        value=data["value"],
        memo=data.get("memo", ""),
    )


def _firestore_error(message: str) -> AppException:
    return AppException(status_code=503, detail=message)


def create_study_data(payload: StudyDataInput) -> StudyDataResponse:
    """학습시간 문서를 생성합니다."""
    try:
        document = get_data_collection().document()
        data = payload.model_dump()
        document.set(
            {
                **data,
                "created_at": firestore.SERVER_TIMESTAMP,
            }
        )
        return _document_to_response(document.id, data)
    except AppException:
        raise
    except Exception as exception:
        raise _firestore_error("Failed to create study data.") from exception


def list_study_data() -> list[StudyDataResponse]:
    """학습시간 문서를 날짜 내림차순으로 조회합니다."""
    try:
        records = [
            _document_to_response(snapshot.id, snapshot.to_dict() or {})
            for snapshot in get_data_collection().stream()
        ]
        return sorted(records, key=lambda record: record.date, reverse=True)
    except AppException:
        raise
    except Exception as exception:
        raise _firestore_error("Failed to list study data.") from exception


def update_study_data(
    document_id: str,
    payload: StudyDataInput,
) -> StudyDataResponse:
    """기존 학습시간 문서를 수정합니다."""
    try:
        document = get_data_collection().document(document_id)
        if not document.get().exists:
            raise AppException(status_code=404, detail="Study data not found.")

        data = payload.model_dump()
        document.update(data)
        return _document_to_response(document_id, data)
    except AppException:
        raise
    except Exception as exception:
        raise _firestore_error("Failed to update study data.") from exception


def delete_study_data(document_id: str) -> None:
    """기존 학습시간 문서를 삭제합니다."""
    try:
        document = get_data_collection().document(document_id)
        if not document.get().exists:
            raise AppException(status_code=404, detail="Study data not found.")

        document.delete()
    except AppException:
        raise
    except Exception as exception:
        raise _firestore_error("Failed to delete study data.") from exception


def summarize_study_data() -> StudyDataSummaryResponse:
    """저장된 학습시간의 기본 통계와 최근 추세를 계산합니다."""
    records = list_study_data()
    if not records:
        return StudyDataSummaryResponse(
            count=0,
            total_minutes=0,
            average_minutes=0,
            max_minutes=0,
            min_minutes=0,
            recent_7_days_total=0,
            recent_trend="not_enough_data",
        )

    values = [record.value for record in records]
    total_minutes = sum(values)
    today = date.today()
    seven_days_ago = today - timedelta(days=6)
    recent_7_days_total = sum(
        record.value
        for record in records
        if seven_days_ago
        <= datetime.strptime(record.date, "%Y-%m-%d").date()
        <= today
    )

    if len(records) < 2:
        recent_trend = "not_enough_data"
    elif records[0].value > records[1].value:
        recent_trend = "increasing"
    elif records[0].value < records[1].value:
        recent_trend = "decreasing"
    else:
        recent_trend = "stable"

    return StudyDataSummaryResponse(
        count=len(records),
        total_minutes=total_minutes,
        average_minutes=round(total_minutes / len(records), 2),
        max_minutes=max(values),
        min_minutes=min(values),
        recent_7_days_total=recent_7_days_total,
        recent_trend=recent_trend,
    )
