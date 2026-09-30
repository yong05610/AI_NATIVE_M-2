"""OpenAI 연결을 애플리케이션과 분리해 확인하는 진단 스크립트입니다.

실행 방법 (backend 디렉터리):
    python scripts/check_openai.py
"""

import os
import re
import sys
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from openai import OpenAI


PROJECT_ROOT = Path(__file__).resolve().parents[2]
ENV_FILE = PROJECT_ROOT / ".env"
MODEL = "gpt-4o-mini"
OUTPUT_LIMIT = 200


def safe_text(value: Any, api_key: str) -> str | None:
    """진단 출력에서 API 키를 제거하고 출력 길이를 제한합니다."""
    if value is None:
        return None

    text = value if isinstance(value, str) else repr(value)
    if api_key:
        text = text.replace(api_key, "[REDACTED]")
    text = re.sub(r"\bsk-[A-Za-z0-9_-]+\b", "[REDACTED]", text)
    return text[:OUTPUT_LIMIT]


def get_error_code(exception: Exception) -> Any:
    """SDK 예외 속성 또는 body에서 오류 코드를 찾습니다."""
    code = getattr(exception, "code", None)
    body = getattr(exception, "body", None)
    if code is None and isinstance(body, dict):
        code = body.get("code")
    return code


def main() -> int:
    """환경변수 확인 후 짧은 OpenAI 요청을 한 번 실행합니다."""
    load_dotenv(dotenv_path=ENV_FILE)
    api_key = (os.getenv("OPENAI_API_KEY") or "").strip()
    print(f"OPENAI_API_KEY configured: {'yes' if api_key else 'no'}")

    if not api_key:
        print("OpenAI diagnostic aborted: OPENAI_API_KEY is not configured.")
        return 1

    try:
        client = OpenAI(api_key=api_key)
        completion = client.chat.completions.create(
            model=MODEL,
            messages=[
                {
                    "role": "user",
                    "content": "연결 확인용으로 한국어 한 문장만 답해주세요.",
                }
            ],
            max_tokens=30,
        )
        answer = completion.choices[0].message.content or ""
        print(f"OpenAI diagnostic succeeded: {safe_text(answer.strip(), api_key)}")
        return 0
    except Exception as exception:
        status_code = getattr(exception, "status_code", None)
        if status_code is None:
            status_code = getattr(exception, "status", None)
        message = getattr(exception, "message", None) or str(exception)
        print(f"Exception class: {type(exception).__name__}")
        print(f"status_code: {status_code}")
        print(f"code: {safe_text(get_error_code(exception), api_key)}")
        print(f"message: {safe_text(message, api_key)}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
