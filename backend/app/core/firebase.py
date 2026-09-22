"""환경변수 기반 Firebase Admin SDK 초기화입니다."""

from threading import Lock

import firebase_admin
from firebase_admin import credentials, firestore

from app.core.config import Settings, get_settings
from app.core.exceptions import AppException


_firebase_initialization_lock = Lock()


def _service_account_info(settings: Settings) -> dict[str, str]:
    values = {
        "FIREBASE_PROJECT_ID": settings.firebase_project_id,
        "FIREBASE_CLIENT_EMAIL": settings.firebase_client_email,
        "FIREBASE_PRIVATE_KEY": settings.firebase_private_key,
    }
    missing_variables = [name for name, value in values.items() if not value]
    if missing_variables:
        missing = ", ".join(missing_variables)
        raise AppException(
            status_code=503,
            detail=f"Firebase configuration is incomplete. Missing: {missing}",
        )

    return {
        "type": "service_account",
        "project_id": settings.firebase_project_id,
        "private_key": settings.firebase_private_key,
        "client_email": settings.firebase_client_email,
        "token_uri": "https://oauth2.googleapis.com/token",
    }


def get_firebase_app():
    """기본 Firebase 앱을 한 번만 초기화해 반환합니다."""
    try:
        return firebase_admin.get_app()
    except ValueError:
        pass

    with _firebase_initialization_lock:
        try:
            return firebase_admin.get_app()
        except ValueError:
            settings = get_settings()
            try:
                credential = credentials.Certificate(_service_account_info(settings))
                return firebase_admin.initialize_app(
                    credential,
                    {"projectId": settings.firebase_project_id},
                )
            except AppException:
                raise
            except Exception as exception:
                raise AppException(
                    status_code=503,
                    detail=(
                        "Firebase initialization failed. "
                        "Check Firebase environment variables."
                    ),
                ) from exception


def get_firestore_client():
    """초기화된 Firebase 앱의 Firestore 클라이언트를 반환합니다."""
    try:
        return firestore.client(app=get_firebase_app())
    except AppException:
        raise
    except Exception as exception:
        raise AppException(
            status_code=503,
            detail="Firestore client creation failed.",
        ) from exception
