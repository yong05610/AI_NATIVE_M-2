"""애플리케이션 공통 예외와 처리 함수입니다."""

from fastapi import Request
from fastapi.responses import JSONResponse


class AppException(Exception):
    """예상 가능한 애플리케이션 오류의 기본 예외입니다."""

    def __init__(self, status_code: int, detail: str) -> None:
        self.status_code = status_code
        self.detail = detail
        super().__init__(detail)


async def app_exception_handler(
    _request: Request,
    exception: AppException,
) -> JSONResponse:
    """AppException을 일관된 JSON 오류 응답으로 변환합니다."""
    return JSONResponse(
        status_code=exception.status_code,
        content={"detail": exception.detail},
    )
