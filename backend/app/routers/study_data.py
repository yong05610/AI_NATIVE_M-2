"""학습시간 데이터 CRUD 및 요약 API 라우터입니다."""

from fastapi import APIRouter

from app.models.common import ErrorResponse, MessageResponse
from app.models.study_data import (
    StudyDataInput,
    StudyDataResponse,
    StudyDataSummaryResponse,
)
from app.services.study_data_service import (
    create_study_data,
    delete_study_data,
    list_study_data,
    summarize_study_data,
    update_study_data,
)


router = APIRouter(prefix="/api/data", tags=["study-data"])


@router.post(
    "",
    response_model=StudyDataResponse,
    responses={503: {"model": ErrorResponse}},
)
def create_data(payload: StudyDataInput) -> StudyDataResponse:
    return create_study_data(payload)


@router.get(
    "",
    response_model=list[StudyDataResponse],
    responses={503: {"model": ErrorResponse}},
)
def get_data() -> list[StudyDataResponse]:
    return list_study_data()


@router.get(
    "/summary",
    response_model=StudyDataSummaryResponse,
    responses={503: {"model": ErrorResponse}},
)
def get_data_summary() -> StudyDataSummaryResponse:
    return summarize_study_data()


@router.put(
    "/{document_id}",
    response_model=StudyDataResponse,
    responses={404: {"model": ErrorResponse}, 503: {"model": ErrorResponse}},
)
def update_data(
    document_id: str,
    payload: StudyDataInput,
) -> StudyDataResponse:
    return update_study_data(document_id, payload)


@router.delete(
    "/{document_id}",
    response_model=MessageResponse,
    responses={404: {"model": ErrorResponse}, 503: {"model": ErrorResponse}},
)
def delete_data(document_id: str) -> MessageResponse:
    delete_study_data(document_id)
    return MessageResponse(message="Data deleted successfully")
