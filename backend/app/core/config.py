"""환경변수 기반 애플리케이션 설정입니다."""

import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv


DEFAULT_FRONTEND_ORIGINS = (
    "http://localhost:5500",
    "http://127.0.0.1:5500",
)
PROJECT_ROOT = Path(__file__).resolve().parents[3]
ENV_FILE = PROJECT_ROOT / ".env"


@dataclass(frozen=True)
class Settings:
    """현재 단계에서 사용하는 애플리케이션 설정입니다."""

    allowed_origins: tuple[str, ...]
    firebase_project_id: str | None
    firebase_client_email: str | None
    firebase_private_key: str | None


def _parse_origins(raw_origins: str | None) -> tuple[str, ...]:
    configured_origins = (
        origin.strip().rstrip("/")
        for origin in (raw_origins or "").split(",")
    )
    origins = [*DEFAULT_FRONTEND_ORIGINS, *filter(None, configured_origins)]
    return tuple(dict.fromkeys(origins))


@lru_cache
def get_settings() -> Settings:
    """프로젝트 루트 .env와 프로세스 환경변수에서 설정을 읽습니다."""
    load_dotenv(dotenv_path=ENV_FILE)
    firebase_private_key = os.getenv("FIREBASE_PRIVATE_KEY")
    return Settings(
        allowed_origins=_parse_origins(os.getenv("FRONTEND_ORIGIN")),
        firebase_project_id=os.getenv("FIREBASE_PROJECT_ID"),
        firebase_client_email=os.getenv("FIREBASE_CLIENT_EMAIL"),
        firebase_private_key=(
            firebase_private_key.replace("\\n", "\n")
            if firebase_private_key
            else None
        ),
    )
