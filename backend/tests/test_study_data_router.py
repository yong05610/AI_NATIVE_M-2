from unittest.mock import Mock

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.core.exceptions import AppException, app_exception_handler
from app.models.study_data import StudyDataResponse, StudyDataSummaryResponse
from app.routers import study_data as study_data_router


@pytest.fixture
def client():
    application = FastAPI()
    application.add_exception_handler(AppException, app_exception_handler)
    application.include_router(study_data_router.router)

    with TestClient(application) as test_client:
        yield test_client


def test_create_data_returns_created_record(client, monkeypatch):
    created_record = StudyDataResponse(
        id="study-1",
        date="2025-01-01",
        value=90,
        memo="수학 공부",
    )
    create_data = Mock(return_value=created_record)
    monkeypatch.setattr(study_data_router, "create_study_data", create_data)

    response = client.post(
        "/api/data",
        json={"date": "2025-01-01", "value": 90, "memo": "수학 공부"},
    )

    assert response.status_code == 200
    assert response.json() == created_record.model_dump()
    create_data.assert_called_once()
    payload = create_data.call_args.args[0]
    assert payload.date == "2025-01-01"
    assert payload.value == 90
    assert payload.memo == "수학 공부"


def test_get_data_returns_record_list(client, monkeypatch):
    records = [
        StudyDataResponse(
            id="study-2",
            date="2025-01-02",
            value=120,
            memo="영어 공부",
        ),
        StudyDataResponse(
            id="study-1",
            date="2025-01-01",
            value=90,
            memo="수학 공부",
        ),
    ]
    list_data = Mock(return_value=records)
    monkeypatch.setattr(study_data_router, "list_study_data", list_data)

    response = client.get("/api/data")

    assert response.status_code == 200
    assert response.json() == [record.model_dump() for record in records]
    assert len(response.json()) == 2
    list_data.assert_called_once_with()


def test_get_data_summary_returns_statistics(client, monkeypatch):
    summary = StudyDataSummaryResponse(
        count=2,
        total_minutes=210,
        average_minutes=105,
        max_minutes=120,
        min_minutes=90,
        recent_7_days_total=210,
        recent_trend="increasing",
    )
    summarize_data = Mock(return_value=summary)
    monkeypatch.setattr(
        study_data_router,
        "summarize_study_data",
        summarize_data,
    )

    response = client.get("/api/data/summary")

    assert response.status_code == 200
    assert response.json() == summary.model_dump()
    summarize_data.assert_called_once_with()


def test_update_data_returns_updated_record(client, monkeypatch):
    updated_record = StudyDataResponse(
        id="study-1",
        date="2025-01-02",
        value=120,
        memo="영어 공부",
    )
    update_data = Mock(return_value=updated_record)
    monkeypatch.setattr(study_data_router, "update_study_data", update_data)

    response = client.put(
        "/api/data/study-1",
        json={"date": "2025-01-02", "value": 120, "memo": "영어 공부"},
    )

    assert response.status_code == 200
    assert response.json() == updated_record.model_dump()
    update_data.assert_called_once()
    document_id, payload = update_data.call_args.args
    assert document_id == "study-1"
    assert payload.date == "2025-01-02"
    assert payload.value == 120
    assert payload.memo == "영어 공부"


def test_delete_data_returns_success_message(client, monkeypatch):
    delete_data = Mock()
    monkeypatch.setattr(study_data_router, "delete_study_data", delete_data)

    response = client.delete("/api/data/study-1")

    assert response.status_code == 200
    assert response.json() == {"message": "Data deleted successfully"}
    delete_data.assert_called_once_with("study-1")


def test_update_data_returns_404_when_record_missing(client, monkeypatch):
    update_data = Mock(
        side_effect=AppException(
            status_code=404,
            detail="Study data not found.",
        )
    )
    monkeypatch.setattr(study_data_router, "update_study_data", update_data)

    response = client.put(
        "/api/data/missing",
        json={"date": "2025-01-02", "value": 120, "memo": "영어 공부"},
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Study data not found."}
    update_data.assert_called_once()
    assert update_data.call_args.args[0] == "missing"


def test_delete_data_returns_404_when_record_missing(client, monkeypatch):
    delete_data = Mock(
        side_effect=AppException(
            status_code=404,
            detail="Study data not found.",
        )
    )
    monkeypatch.setattr(study_data_router, "delete_study_data", delete_data)

    response = client.delete("/api/data/missing")

    assert response.status_code == 404
    assert response.json() == {"detail": "Study data not found."}
    delete_data.assert_called_once_with("missing")


def test_create_data_rejects_invalid_value(client, monkeypatch):
    create_data = Mock()
    monkeypatch.setattr(study_data_router, "create_study_data", create_data)

    response = client.post(
        "/api/data",
        json={"date": "2025-01-01", "value": -10, "memo": "잘못된 데이터"},
    )

    assert response.status_code == 422
    create_data.assert_not_called()
