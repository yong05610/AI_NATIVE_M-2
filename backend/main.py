"""FastAPI 애플리케이션 실행 진입점입니다."""

from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from app.core.config import get_settings
from app.core.exceptions import AppException, app_exception_handler
from app.routers.health import router as health_router
from app.routers.study_data import router as study_data_router


load_dotenv(dotenv_path=Path(__file__).parent.parent / ".env")


def create_app() -> FastAPI:
    """애플리케이션과 공통 미들웨어 및 라우터를 구성합니다."""
    settings = get_settings()
    application = FastAPI(
        title="AI Study Time Assistant API",
        version="1.0.0",
        docs_url="/docs",
    )

    application.add_middleware(
        CORSMiddleware,
        allow_origins=list(settings.allowed_origins),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    application.add_exception_handler(AppException, app_exception_handler)
    application.include_router(health_router)
    application.include_router(study_data_router)

    return application


app = create_app()
