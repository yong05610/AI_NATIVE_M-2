from datetime import date, timedelta
from types import SimpleNamespace
from unittest.mock import Mock

import pytest
from firebase_admin import firestore

from app.core.exceptions import AppException
from app.models.study_data import StudyDataInput, StudyDataResponse
from app.services import study_data_service


def _record(
    document_id: str,
    record_date: date,
    value: float,
    memo: str = "",
) -> StudyDataResponse:
    return StudyDataResponse(
        id=document_id,
        date=record_date.isoformat(),
        value=value,
        memo=memo,
    )


def test_summarize_study_data_returns_zeros_when_empty(monkeypatch):
    list_data = Mock(return_value=[])
    monkeypatch.setattr(study_data_service, "list_study_data", list_data)

    summary = study_data_service.summarize_study_data()

    list_data.assert_called_once_with()
    assert summary.count == 0
    assert summary.total_minutes == 0
    assert summary.average_minutes == 0
    assert summary.max_minutes == 0
    assert summary.min_minutes == 0
    assert summary.recent_7_days_total == 0
    assert summary.recent_trend == "not_enough_data"


def test_summarize_study_data_calculates_statistics(monkeypatch):
    today = date.today()
    records = [
        _record("today", today, 120),
        _record("yesterday", today - timedelta(days=1), 60),
        _record("old", today - timedelta(days=10), 30),
    ]
    list_data = Mock(return_value=records)
    monkeypatch.setattr(study_data_service, "list_study_data", list_data)

    summary = study_data_service.summarize_study_data()

    list_data.assert_called_once_with()
    assert summary.count == 3
    assert summary.total_minutes == 210
    assert summary.average_minutes == 70
    assert summary.max_minutes == 120
    assert summary.min_minutes == 30
    assert summary.recent_7_days_total == 180
    assert summary.recent_trend == "increasing"


@pytest.mark.parametrize(
    ("latest_value", "previous_value", "expected_trend"),
    [
        (120, 60, "increasing"),
        (60, 120, "decreasing"),
        (60, 60, "stable"),
    ],
)
def test_summarize_study_data_calculates_recent_trend(
    monkeypatch,
    latest_value,
    previous_value,
    expected_trend,
):
    today = date.today()
    records = [
        _record("latest", today, latest_value),
        _record("previous", today - timedelta(days=1), previous_value),
    ]
    monkeypatch.setattr(
        study_data_service,
        "list_study_data",
        Mock(return_value=records),
    )

    summary = study_data_service.summarize_study_data()

    assert summary.recent_trend == expected_trend


def test_create_study_data_writes_document_and_returns_response(monkeypatch):
    document = Mock()
    document.id = "study-1"
    collection = Mock()
    collection.document.return_value = document
    get_collection = Mock(return_value=collection)
    monkeypatch.setattr(study_data_service, "get_data_collection", get_collection)
    payload = StudyDataInput(
        date="2026-09-25",
        value=120,
        memo="FastAPI 학습",
    )

    result = study_data_service.create_study_data(payload)

    get_collection.assert_called_once_with()
    collection.document.assert_called_once_with()
    document.set.assert_called_once_with(
        {
            "date": "2026-09-25",
            "value": 120.0,
            "memo": "FastAPI 학습",
            "created_at": firestore.SERVER_TIMESTAMP,
        }
    )
    assert result == StudyDataResponse(
        id="study-1",
        date="2026-09-25",
        value=120,
        memo="FastAPI 학습",
    )


def test_list_study_data_converts_and_sorts_documents(monkeypatch):
    snapshots = [
        SimpleNamespace(
            id="older",
            to_dict=Mock(
                return_value={"date": "2026-09-20", "value": 30, "memo": "old"}
            ),
        ),
        SimpleNamespace(
            id="newer",
            to_dict=Mock(
                return_value={"date": "2026-09-25", "value": 60, "memo": "new"}
            ),
        ),
    ]
    collection = Mock()
    collection.stream.return_value = snapshots
    monkeypatch.setattr(
        study_data_service,
        "get_data_collection",
        Mock(return_value=collection),
    )

    records = study_data_service.list_study_data()

    collection.stream.assert_called_once_with()
    assert [record.id for record in records] == ["newer", "older"]
    assert [record.date for record in records] == ["2026-09-25", "2026-09-20"]
    assert records[0].memo == "new"


def test_update_study_data_updates_existing_document(monkeypatch):
    document = Mock()
    document.get.return_value = SimpleNamespace(exists=True)
    collection = Mock()
    collection.document.return_value = document
    monkeypatch.setattr(
        study_data_service,
        "get_data_collection",
        Mock(return_value=collection),
    )
    payload = StudyDataInput(date="2026-09-25", value=90, memo="수정")

    result = study_data_service.update_study_data("study-1", payload)

    collection.document.assert_called_once_with("study-1")
    document.update.assert_called_once_with(
        {"date": "2026-09-25", "value": 90.0, "memo": "수정"}
    )
    assert result == StudyDataResponse(
        id="study-1",
        date="2026-09-25",
        value=90,
        memo="수정",
    )


def test_update_study_data_returns_404_when_document_missing(monkeypatch):
    document = Mock()
    document.get.return_value = SimpleNamespace(exists=False)
    collection = Mock()
    collection.document.return_value = document
    monkeypatch.setattr(
        study_data_service,
        "get_data_collection",
        Mock(return_value=collection),
    )
    payload = StudyDataInput(date="2026-09-25", value=90, memo="수정")

    with pytest.raises(AppException) as exception_info:
        study_data_service.update_study_data("missing", payload)

    assert exception_info.value.status_code == 404
    assert exception_info.value.detail == "Study data not found."
    document.update.assert_not_called()


def test_delete_study_data_deletes_existing_document(monkeypatch):
    document = Mock()
    document.get.return_value = SimpleNamespace(exists=True)
    collection = Mock()
    collection.document.return_value = document
    monkeypatch.setattr(
        study_data_service,
        "get_data_collection",
        Mock(return_value=collection),
    )

    study_data_service.delete_study_data("study-1")

    collection.document.assert_called_once_with("study-1")
    document.delete.assert_called_once_with()


def test_delete_study_data_returns_404_when_document_missing(monkeypatch):
    document = Mock()
    document.get.return_value = SimpleNamespace(exists=False)
    collection = Mock()
    collection.document.return_value = document
    monkeypatch.setattr(
        study_data_service,
        "get_data_collection",
        Mock(return_value=collection),
    )

    with pytest.raises(AppException) as exception_info:
        study_data_service.delete_study_data("missing")

    assert exception_info.value.status_code == 404
    assert exception_info.value.detail == "Study data not found."
    document.delete.assert_not_called()
