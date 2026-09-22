## 0.공통
MISSION.md, PRD.md, docs/TASK.md, docs/CHECKLIST.md를 기준으로 구현해줘.

중요 기준:
- 공식 요약 API 경로는 GET /api/data/summary
- Firestore 컬렉션명은 data, conversations
- conversations 문서 1개는 message, answer, created_at 구조
- messages 배열 기반 다중 턴 구조는 사용하지 않음
- 프론트엔드에서 AI 질문 시 POST /api/chat만 호출하고 POST /api/conversations를 추가 호출하지 않음
- Python 3.11 이상 권장, Python 3.12 검증, Python 3.14 제외, 프로젝트 루트 `.venv`, `python -m pip`, `requirements.txt` 기준
- 민감정보는 코드에 직접 작성하지 않고 환경변수로 처리
- OpenAI API Key와 Firebase 인증정보는 프론트엔드에 절대 노출하지 않음
- 한 번에 과도하게 구현하지 말고 이번 요청 범위만 작업

## Section 1. 프로젝트 초기설정
MISSION.md, PRD.md, docs/TASK.md, docs/CHECKLIST.md를 기준으로 TASK.md의 "1. 프로젝트 초기 설정"을 구현해줘.

이번 작업 범위:
- Python 3.11 이상(Python 3.12 검증, Python 3.14 제외) 기준 프로젝트 디렉터리 구조 생성
- backend와 frontend 소스 위치 분리
- backend/requirements.txt 작성
- .env.example 작성
- .gitignore 작성 또는 보완
- README.md에 로컬 실행 준비 단계 최소 반영

필수 패키지:
- fastapi
- uvicorn
- firebase-admin
- openai
- python-dotenv

원하는 구조 예시:
backend/
  main.py
  requirements.txt
  app/
    __init__.py
    core/
    models/
    routers/
    services/

frontend/
  index.html
  styles.css
  app.js

환경변수 예시:
- OPENAI_API_KEY
- FIREBASE_PROJECT_ID
- FIREBASE_CLIENT_EMAIL
- FIREBASE_PRIVATE_KEY
- FRONTEND_ORIGIN

중요:
- 실제 API 키, Firebase 키, 서비스 계정 JSON 등 민감정보는 절대 작성하지 마.
- .env는 .gitignore에 포함해.
- .env.example에는 예시 값만 작성해.
- 아직 Firestore 연결, CRUD API, OpenAI 호출은 구현하지 마.

완료 후 다음 형식으로 보고해줘.

1. 생성/수정한 파일
2. 프로젝트 구조
3. 설치 방법
4. 아직 구현하지 않은 항목
5. 다음 단계 제안
## Section 2.  백엔드 기본 구조 구현
MISSION.md, PRD.md, docs/TASK.md, docs/CHECKLIST.md를 기준으로 TASK.md의 "2. 백엔드 기본 구조 구현"을 구현해줘.

이번 작업 범위:
- FastAPI 애플리케이션 생성
- 실행 진입점 구현
- GET / 기본 상태 확인 API 구현
- CORS 설정
- Swagger UI /docs 접속 가능 상태 확인
- 기본 Pydantic 모델 및 공통 오류 처리 구조 준비

필수 동작:
- uvicorn main:app --reload 로 실행 가능해야 함
- GET / 응답은 다음과 같아야 함:
  {"message": "AI Study Time Assistant API"}
- /docs 에서 Swagger UI가 보여야 함
- FRONTEND_ORIGIN 환경변수를 읽어 CORS에 반영할 수 있어야 함
- 로컬 개발용 origin도 허용할 수 있어야 함

주의:
- 이번 단계에서는 Firestore 연결은 구현하지 마.
- 이번 단계에서는 데이터 CRUD, AI 채팅, 대화 기록 API는 구현하지 마.
- 단, 이후 라우터를 추가하기 쉬운 구조로 작성해.
- 코드 구조는 학습자가 이해하기 쉽게 단순하게 유지해.

완료 후 다음 형식으로 보고해줘.

1. 생성/수정한 파일
2. 실행 방법
3. 확인 가능한 API
4. Swagger 확인 방법
5. 아직 구현하지 않은 항목
6. 다음 단계 제안
## Section 3. Firestore 연동
MISSION.md, PRD.md, docs/TASK.md, docs/CHECKLIST.md를 기준으로 TASK.md의 "3. Firestore 연동"을 구현해줘.

이번 작업 범위:
- Firebase Admin SDK 초기화
- 환경변수 기반 Firestore 클라이언트 생성
- GET /api/health/firestore 구현
- data 컬렉션과 conversations 컬렉션 접근 구조 준비

환경변수 기준:
- FIREBASE_PROJECT_ID
- FIREBASE_CLIENT_EMAIL
- FIREBASE_PRIVATE_KEY

필수 API:
GET /api/health/firestore

정상 응답:
{
  "status": "ok",
  "message": "Firestore connected"
}

중요:
- Firebase 서비스 계정 정보는 코드에 하드코딩하지 마.
- FIREBASE_PRIVATE_KEY의 줄바꿈 문제를 처리할 수 있게 해줘.
- 환경변수가 누락되었거나 연결 실패 시 서버가 죽지 않고 명확한 오류를 반환하게 해줘.
- 컬렉션명은 반드시 data, conversations를 사용해.
- conversations는 message, answer, created_at 구조를 기준으로 해.
- messages 배열 구조는 사용하지 마.

주의:
- 아직 데이터 CRUD API 전체 구현은 하지 마.
- 아직 OpenAI 연동은 하지 마.
- Firestore 연결 확인과 클라이언트 구조까지만 구현해.

완료 후 다음 형식으로 보고해줘.

1. 생성/수정한 파일
2. 필요한 환경변수
3. 실행 방법
4. 확인한 API
5. 실패 시 확인할 점
6. 다음 단계 제안
## Section 4. 학습시간 데이터 API 구현
MISSION.md, PRD.md, docs/TASK.md, docs/CHECKLIST.md를 기준으로 TASK.md의 "4. 학습시간 데이터 API 구현"을 구현해줘.

이번 작업 범위:
학습시간 데이터 CRUD API와 요약 API를 구현해줘.

필수 엔드포인트:
- POST /api/data
- GET /api/data
- PUT /api/data/{id}
- DELETE /api/data/{id}
- GET /api/data/summary

data 컬렉션 문서 구조:
{
  "date": "2025-01-10",
  "value": 120,
  "memo": "FastAPI 기초 학습",
  "created_at": "2025-01-10T12:00:00Z"
}

입력 검증:
- date는 필수
- date는 YYYY-MM-DD 형식
- value는 필수
- value는 0보다 큰 숫자
- memo는 선택 가능

POST /api/data 응답:
{
  "id": "...",
  "date": "...",
  "value": 120,
  "memo": "..."
}

GET /api/data 응답:
- id, date, value, memo를 포함한 배열
- 가능하면 날짜 내림차순 정렬
- 데이터가 없으면 오류 없이 빈 배열 반환

PUT /api/data/{id}:
- date, value, memo 수정
- 존재하지 않는 id는 적절한 오류 반환

DELETE /api/data/{id}:
정상 응답:
{
  "message": "Data deleted successfully"
}

GET /api/data/summary 응답:
{
  "count": 10,
  "total_minutes": 900,
  "average_minutes": 90,
  "max_minutes": 180,
  "min_minutes": 30,
  "recent_7_days_total": 520,
  "recent_trend": "increasing"
}

recent_trend 값:
- increasing
- decreasing
- stable
- not_enough_data

중요:
- 요약 API 공식 경로는 반드시 GET /api/data/summary
- GET /api/summary는 만들지 마.
- 데이터가 없을 때도 0 나누기 오류가 나면 안 됨.
- Firestore 오류가 발생해도 서버가 중단되지 않게 처리해.
- OpenAI 채팅 기능은 아직 구현하지 마.
- 대화 기록 API도 아직 구현하지 마.

완료 후 다음 형식으로 보고해줘.

1. 생성/수정한 파일
2. 구현한 API 목록
3. 요청/응답 예시
4. Swagger에서 검증하는 방법
5. 예외 처리 내용
6. 다음 단계 제안
## Section 5. AI 대화 기능 구현
MISSION.md, PRD.md, docs/TASK.md, docs/CHECKLIST.md를 기준으로 TASK.md의 "5. AI 대화 기능 구현"을 구현해줘.

이번 작업 범위:
- POST /api/chat 구현
- 학습시간 요약을 AI 시스템 프롬프트에 주입
- OpenAI API 호출
- AI 응답 반환
- 생성된 질문과 답변을 conversations 컬렉션에 자동 저장

필수 엔드포인트:
POST /api/chat

요청 예시:
{
  "message": "최근 학습 흐름이 어때?"
}

응답 예시:
{
  "answer": "최근 기록을 보면 학습 시간이 증가하는 흐름입니다..."
}

AI 동작 요구:
- Firestore data 컬렉션의 학습시간 데이터를 기반으로 요약을 생성하거나 기존 summary 로직을 재사용
- 요약 정보를 시스템 프롬프트에 포함
- 사용자의 실제 학습 기록을 근거로 답변
- 학습 코치처럼 친절하고 구체적으로 답변
- 너무 길지 않게 핵심 위주로 답변
- 다음 행동 제안 포함
- 데이터가 부족하면 부족하다는 점을 말하고 일반적인 조언 제공

OpenAI 관련:
- OPENAI_API_KEY는 환경변수에서 읽기
- 프론트엔드에 API 키 노출 금지
- 개발/테스트 비용을 고려해 max_tokens 등 출력 제한 설정
- OpenAI 호출 실패 시 명확한 오류 반환

대화 자동 저장:
- POST /api/chat이 성공하면 conversations 컬렉션에 자동 저장
- 저장 구조:
{
  "message": "사용자 질문",
  "answer": "AI 답변",
  "created_at": "..."
}
- 채팅 응답 한 번당 conversations 문서는 정확히 1개만 생성

중요:
- 프론트엔드에서 POST /api/chat 이후 POST /api/conversations를 추가 호출하지 않는 구조를 전제로 해.
- conversations 컬렉션에 messages 배열 구조를 만들지 마.
- 이번 단계에서는 대화 목록 조회/상세조회/삭제 API는 아직 구현하지 않아도 됨.
- 기존 데이터 CRUD와 요약 API가 깨지지 않게 해.

완료 후 다음 형식으로 보고해줘.

1. 생성/수정한 파일
2. 구현한 API
3. AI 프롬프트 구성 방식
4. 대화 자동 저장 방식
5. 테스트 방법
6. 비용/환경변수 주의사항
7. 다음 단계 제안
## Section 6. 대화 기록 API 구현
MISSION.md, PRD.md, docs/TASK.md, docs/CHECKLIST.md를 기준으로 TASK.md의 "6. 대화 기록 API 구현"을 구현해줘.

이번 작업 범위:
AI 대화 기록 저장, 목록 조회, 상세 조회, 삭제 API를 구현해줘.

필수 엔드포인트:
- POST /api/conversations
- GET /api/conversations
- GET /api/conversations/{id}
- DELETE /api/conversations/{id}

conversations 컬렉션 문서 구조:
{
  "message": "최근 학습 흐름이 어때?",
  "answer": "최근 기록을 보면 학습 시간이 증가하는 흐름입니다.",
  "created_at": "2025-01-10T12:30:00Z"
}

POST /api/conversations:
- Swagger 또는 API 클라이언트에서 직접 저장할 수 있는 용도
- message와 answer가 모두 있어야 저장
- 응답에는 id, message, answer, created_at 포함

GET /api/conversations:
- 저장된 대화 목록 반환
- id, message, answer, created_at 포함
- 최신 대화가 먼저 오도록 정렬 권장
- 기록이 없으면 빈 배열 반환

GET /api/conversations/{id}:
- 특정 대화의 질문과 답변을 반환
- 프론트엔드의 대화 불러오기 기능에서 사용
- 존재하지 않는 id는 적절한 오류 반환

DELETE /api/conversations/{id}:
정상 응답:
{
  "message": "Conversation deleted successfully"
}

중요:
- conversations 문서 1개는 질문 1개와 답변 1개만 포함
- messages 배열 구조는 사용하지 마.
- chats 컬렉션은 사용하지 마.
- POST /api/chat의 자동 저장 로직과 중복되거나 충돌하지 않게 해.
- 프론트엔드 AI 질문 흐름에서는 POST /api/conversations를 호출하지 않는다는 점을 주석 또는 구조로 명확히 해도 좋음.

완료 후 다음 형식으로 보고해줘.

1. 생성/수정한 파일
2. 구현한 API 목록
3. 요청/응답 예시
4. Swagger 검증 방법
5. POST /api/chat 자동 저장과의 관계
6. 다음 단계 제안
## Section 7. 프론트엔드 구현
MISSION.md, PRD.md, docs/TASK.md, docs/CHECKLIST.md를 기준으로 TASK.md의 "7. 프론트엔드 구현"을 구현해줘.

이번 작업 범위:
HTML, CSS, Vanilla JavaScript 기반 단일 페이지 프론트엔드를 구현해줘.

필수 파일:
frontend/
  index.html
  styles.css
  app.js

프레임워크 사용 금지:
- React, Vue, Next.js 등 사용하지 마.
- HTML/CSS/Vanilla JavaScript만 사용해.

필수 화면 영역:
1. 헤더 영역
2. 학습시간 입력 영역
3. 학습 통계 요약 영역
4. 학습기록 목록 영역
5. AI 질문 입력 영역
6. AI 답변 영역
7. AI 대화 기록 영역

필수 API 호출:
- POST /api/data
- GET /api/data
- PUT /api/data/{id}
- DELETE /api/data/{id}
- GET /api/data/summary
- POST /api/chat
- GET /api/conversations
- GET /api/conversations/{id}
- DELETE /api/conversations/{id}는 가능하면 버튼으로 제공하거나 최소 API 구조와 연결 가능하게 구현

학습시간 등록:
- 날짜, 학습시간, 메모 입력
- 등록 버튼 클릭 시 POST /api/data 호출
- 성공 시 입력 폼 초기화
- 성공 시 목록과 요약 통계 갱신
- 실패 시 오류 메시지 표시

학습시간 수정:
- 목록의 각 항목에 수정 버튼 표시
- 수정 버튼 클릭 시 기존 date, value, memo가 입력 폼에 채워짐
- 수정 상태에서 저장하면 PUT /api/data/{id} 호출
- 수정 성공 후 목록과 요약 통계 갱신
- 수정 취소 또는 등록 모드 복귀가 가능하면 좋음

학습시간 삭제:
- 삭제 버튼 클릭 시 DELETE /api/data/{id} 호출
- 성공 후 목록과 요약 통계 갱신

요약 통계:
- 페이지 로드 시 GET /api/data/summary 호출
- 등록/수정/삭제 후 다시 호출
- count, total_minutes, average_minutes, max_minutes, min_minutes, recent_7_days_total, recent_trend 표시

AI 질문:
- 질문 버튼 클릭 시 POST /api/chat만 호출
- 로딩 상태 표시
- 사용자 질문과 AI 답변 표시
- 응답 후 대화 기록 목록 갱신
- 절대 POST /api/conversations를 추가 호출하지 마. 중복 저장 방지 필요.

대화 기록:
- 페이지 로드 시 GET /api/conversations 호출
- 대화 목록에 질문, 답변, 생성 시간 표시
- 이전 대화 클릭 시 GET /api/conversations/{id} 호출
- 선택한 대화의 질문과 답변을 채팅창에 복원

API 주소:
- 로컬과 배포 환경에서 API_BASE_URL을 쉽게 바꿀 수 있게 상단 상수 또는 설정 구조로 작성
- README에 변경 방법을 적어도 좋음

오류 처리:
- API 실패 시 화면에 사용자가 이해할 수 있는 메시지 표시
- 화면이 멈추지 않게 처리

중요:
- OpenAI API Key와 Firebase 정보는 프론트엔드에 절대

