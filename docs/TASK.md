# TASK.md

## 1. 프로젝트 초기 설정

- [x] Python 3.11 이상 환경과 프로젝트 로컬 가상환경을 구성한다.
  - 작업 내용: Python 3.12를 로컬 검증 권장 버전으로 사용하고 프로젝트 루트의 `.venv`에서만 개발한다. Python 3.14는 현재 프로젝트의 검증 대상에서 제외한다.
  - 완료 기준: `py -3.12 -m venv .venv`로 가상환경을 생성하고 `.\.venv\Scripts\Activate.ps1`로 활성화할 수 있으며, `python --version`이 Python 3.12.x 또는 허용 범위인 Python 3.11 이상이다. `python -m pip --version` 경로에 `.venv`가 포함된다.
- [x] 필수 패키지와 의존성 파일을 준비한다.
  - 작업 내용: `fastapi`, `uvicorn`, `firebase-admin`, `openai`, `python-dotenv`, `pytest`를 설치하고 `requirements.txt`에 기록한다.
  - 완료 기준: 활성화된 `.venv`에서 `python -m pip install -r backend/requirements.txt`로 패키지를 설치할 수 있다.
- [x] 환경변수 파일 구조를 준비한다.
  - 작업 내용: `OPENAI_API_KEY`, `FIREBASE_PROJECT_ID`, `FIREBASE_CLIENT_EMAIL`, `FIREBASE_PRIVATE_KEY`, `FRONTEND_ORIGIN`을 로컬 및 배포 환경에서 주입할 수 있게 하고, 예시 값만 포함한 `.env.example`을 작성한다.
  - 완료 기준: 실제 비밀값이 소스 코드와 Git에 포함되지 않고 `.env`가 `.gitignore`에 등록되어 있다.

## 2. 백엔드 기본 구조 구현

- [x] FastAPI 애플리케이션과 실행 진입점을 구현한다.
  - 완료 기준: 활성화된 `.venv`에서 `python -m uvicorn main:app --reload`로 서버가 실행되고 `GET /`이 `{"message": "AI Study Time Assistant API"}`를 반환한다.
- [x] Pydantic 요청 모델과 공통 오류 처리 구조를 구현한다.
  - 완료 기준: 필수값 누락과 잘못된 타입에 대해 검증 오류가 반환되고, 서버 오류가 사용자에게 노출할 수 있는 명확한 메시지로 처리된다.
- [ ] CORS와 Swagger UI를 구성한다.
  - 완료 기준: 로컬 프론트엔드 및 `FRONTEND_ORIGIN`에 설정된 Vercel 도메인의 요청이 허용되고 `/docs`에서 모든 API를 확인할 수 있다.

## 3. Firestore 연동

- [x] Firebase Admin SDK를 환경변수 기반으로 초기화한다.
  - 완료 기준: 서비스 계정 정보가 코드에 하드코딩되지 않고 정상 환경에서 Firestore 클라이언트가 생성된다.
- [x] Firestore 연결 확인 API를 구현한다.
  - 엔드포인트: `GET /api/health/firestore`
  - 요청/응답: 별도 요청 본문 없이 `{"status": "ok", "message": "Firestore connected"}`를 반환한다.
  - 검증 기준: 정상 자격 증명에서는 성공 응답을 반환하고, 환경변수 누락 또는 연결 실패 시 원인을 확인할 수 있는 오류를 반환한다.
- [ ] `data`와 `conversations` 컬렉션 접근 구조를 구현한다.
  - 작업 내용: `data`에는 `date`, `value`, `memo`, `created_at`을 저장한다. `conversations`의 문서 1개에는 질문 1개와 답변 1개를 `message`, `answer`, `created_at`으로 저장한다.
  - 완료 기준: 두 컬렉션에 테스트 문서를 저장하고 다시 조회할 수 있으며, `messages` 배열을 사용하는 다중 턴 구조는 포함하지 않는다.
  - 부분 완료: 두 컬렉션 접근 함수와 문서 구조는 구현 및 mock 테스트가 완료됐으며, 실제 `conversations` 컬렉션 통합 검증은 추후 확인이 필요하다.

## 4. 학습시간 데이터 API 구현

- [x] 학습시간 등록 API를 구현한다.
  - 엔드포인트: `POST /api/data`
  - 요청/응답: `{"date":"2025-01-10","value":120,"memo":"FastAPI 기초 학습"}`를 받아 생성된 `id`, `date`, `value`, `memo`를 반환한다.
  - 검증 기준: `date`는 비어 있지 않은 `YYYY-MM-DD` 형식이고 `value`는 0보다 큰 숫자여야 하며, 정상 요청은 `data` 컬렉션에 저장된다.
- [x] 학습시간 목록 조회 API를 구현한다.
  - 엔드포인트: `GET /api/data`
  - 요청/응답: 요청 본문 없이 `id`, `date`, `value`, `memo`를 포함한 배열을 반환한다.
  - 검증 기준: 저장된 데이터가 목록에 나타나고 가능하면 날짜 내림차순으로 정렬되며, 데이터가 없을 때 빈 배열 또는 안내 응답을 오류 없이 반환한다.
- [x] 학습시간 수정 API를 구현한다.
  - 엔드포인트: `PUT /api/data/{id}`
  - 요청/응답: 수정할 `date`, `value`, `memo`를 받아 `id`와 수정된 필드를 반환한다.
  - 검증 기준: 등록 API와 같은 필드 검증을 적용하고, 수정 후 재조회 시 변경값이 표시되며, 존재하지 않는 `id`에는 적절한 오류를 반환한다.
- [x] 학습시간 삭제 API를 구현한다.
  - 엔드포인트: `DELETE /api/data/{id}`
  - 요청/응답: 경로의 문서 `id`를 삭제하고 `{"message":"Data deleted successfully"}`를 반환한다.
  - 검증 기준: 삭제 후 목록에서 문서가 사라지고, 존재하지 않는 `id`에는 적절한 오류를 반환한다.
- [x] 학습시간 요약 API를 구현한다.
  - 엔드포인트: `GET /api/data/summary`
  - 요청/응답: 요청 본문 없이 `count`, `total_minutes`, `average_minutes`, `max_minutes`, `min_minutes`, `recent_7_days_total`, `recent_trend`를 반환한다.
  - 검증 기준: 저장 데이터로 각 값을 계산하고 `recent_trend`는 `increasing`, `decreasing`, `stable`, `not_enough_data` 중 하나이며, 데이터가 없을 때 `count: 0`으로 0 나누기 오류 없이 응답한다.

## 5. AI 대화 기능 구현

- [x] 학습시간 요약을 AI 시스템 프롬프트에 주입한다.
  - 완료 기준: `POST /api/chat` 처리 시 Firestore 데이터를 조회해 요약을 생성하고, 사용자의 실제 학습 기록을 근거로 답하도록 OpenAI 요청에 포함한다.
- [x] AI 채팅 API를 구현한다.
  - 엔드포인트: `POST /api/chat`
  - 요청/응답: `{"message":"최근 학습 흐름이 어때?"}`를 받아 저장된 대화의 `id`, `message`, `answer`, `created_at`을 반환한다.
  - 검증 기준: 빈 질문을 거부하고, 정상 요청에는 친절하고 구체적인 학습 코치 말투로 너무 길지 않은 답변과 다음 행동을 반환하며, 데이터가 부족하면 그 사실과 일반적인 조언을 안내한다. 개발·테스트 단계에서는 적절한 출력 토큰 제한을 적용한다.
- [x] 생성한 질문과 답변을 `conversations`에 자동 저장한다.
  - 작업 내용: OpenAI 응답 생성 후 같은 요청 흐름 안에서 `message`, `answer`, `created_at`을 한 문서로 저장한다.
  - 완료 기준: 채팅 응답 한 번당 대화 문서가 정확히 한 개 생성되고 질문과 답변이 함께 저장된다.
- [ ] 프론트엔드 채팅 호출의 중복 저장 방지 규칙을 적용한다.
  - 작업 내용: 사용자가 질문할 때 프론트엔드는 `POST /api/chat`만 호출하고, 이후 `POST /api/conversations`를 별도로 호출하지 않는다.
  - 완료 기준: 브라우저에서 질문 한 번을 전송했을 때 `conversations`에 동일한 대화가 중복 저장되지 않는다.

## 6. 대화 기록 API 구현

- [x] 대화 기록 저장 API를 구현한다.
  - 엔드포인트: `POST /api/conversations`
  - 요청/응답: `{"message":"최근 학습 흐름이 어때?","answer":"최근 기록을 보면..."}`를 받아 생성된 `id`, `message`, `answer`, `created_at`을 반환한다.
  - 검증 기준: 질문과 답변이 모두 있는 요청만 저장하고 문서 1개가 질문·답변 1쌍만 포함한다. 이 API는 Swagger 또는 별도 API 클라이언트용이며 프론트엔드의 AI 질문 흐름에서는 호출하지 않는다.
- [x] 대화 기록 목록 조회 API를 구현한다.
  - 엔드포인트: `GET /api/conversations`
  - 요청/응답: 요청 본문 없이 각 항목의 `id`, `message`, `answer`, `created_at`을 포함한 배열을 반환한다.
  - 검증 기준: 최신 대화를 먼저 표시할 수 있는 순서로 반환하고, 기록이 없을 때 빈 배열을 오류 없이 반환한다.
- [x] 특정 대화 기록 불러오기 API를 구현한다.
  - 엔드포인트: `GET /api/conversations/{id}`
  - 요청/응답: 경로의 `id`에 해당하는 `id`, `message`, `answer`, `created_at`을 반환한다.
  - 검증 기준: 선택한 질문과 답변 전체를 반환해 채팅창에 다시 표시할 수 있고, 존재하지 않는 `id`에는 적절한 오류를 반환한다.
- [x] 대화 기록 삭제 API를 구현한다.
  - 엔드포인트: `DELETE /api/conversations/{id}`
  - 요청/응답: 경로의 문서 `id`를 삭제하고 `{"message":"Conversation deleted successfully"}`를 반환한다.
  - 검증 기준: 삭제 후 목록에서 문서가 사라지고, 존재하지 않는 `id`에는 적절한 오류를 반환한다.

## 7. 프론트엔드 구현

### 7.1 프론트엔드 구현 단계 개요

- 단계 0: 요구사항 분석 — 완료
- 단계 1: Vanilla 정적 구조 전환 — 완료
- 단계 2: 학습시간 CRUD 및 요약 연동 — 예정
- 단계 3: AI 채팅 및 대화 기록 연동 — 예정
- 단계 4: UI 안정화 및 사용성 개선 — 예정
- 단계 5: 최종 검증, README, 제출물 정리 — 예정

### 7.2 단계 0. 요구사항 분석

상태: 완료

- [x] `MISSION.md`, `PRD.md`, `docs/TASK.md`, `docs/CHECKLIST.md`, `README.md`를 확인한다.
- [x] 프론트엔드 기술 스택, 필수 화면 영역, 기능 및 배포 요구사항을 확인한다.
- [x] React, TypeScript, Vite, npm 빌드 환경을 제거해야 함을 확인한다.
- [x] HTML, CSS, Vanilla JavaScript 기반 단일 페이지 앱으로 재구현하기로 정리한다.
- [x] 필수 화면 영역과 프론트엔드에서 사용할 필수 API 경로를 확인한다.
- [x] AI 질문 전송 시 `POST /api/chat`만 호출하고 `POST /api/conversations`를 추가 호출하지 않는 규칙을 확인한다.

### 7.3 단계 1. Vanilla 정적 구조 전환

상태: 완료

- [x] React, Vite, TypeScript 관련 파일과 실행 구조를 삭제한다.
- [x] `frontend/index.html`을 생성한다.
- [x] `frontend/styles.css`를 생성한다.
- [x] `frontend/app.js`를 생성한다.
- [x] `frontend/config.example.js`를 생성한다.
- [x] API 호출이 없는 정적 화면 골격을 생성한다.
- [x] README 수정은 이 단계에서 수행하지 않고 단계 5에서 진행하도록 정리한다.

완료 기준:

- React, Vite, TypeScript 관련 실행 구조가 제거되어 있다.
- Vanilla JavaScript 기반 정적 파일 구조가 존재한다.
- `index.html`, `styles.css`, `app.js`가 브라우저에서 로드될 수 있다.
- 이 단계에서는 백엔드 API 연동을 구현하지 않는다.

### 7.4 단계 2. 학습시간 CRUD 및 요약 연동

상태: 예정

수정 허용 파일:

- `frontend/index.html`
- `frontend/styles.css`
- `frontend/app.js`
- `frontend/config.example.js`

구현 범위:

- [ ] API Base URL 설정
- [ ] `GET /api/data`
- [ ] `POST /api/data`
- [ ] `PUT /api/data/{document_id}`
- [ ] `DELETE /api/data/{document_id}`
- [ ] `GET /api/data/summary`
- [ ] 학습시간 입력 폼
- [ ] 학습 통계 요약 표시
- [ ] 학습기록 목록 표시
- [ ] 수정 버튼과 기존 값 채우기
- [ ] 삭제 버튼
- [ ] 등록, 수정, 삭제 후 목록과 요약 갱신
- [ ] API 실패 시 사용자 오류 메시지 표시

금지 사항:

- `POST /api/chat` 구현 금지
- `/api/conversations` 연동 금지
- `README.md` 수정 금지
- `CHECKLIST.md` 수정 금지
- `backend`, `docs`의 다른 섹션, `.github`, `scripts` 수정 금지

완료 기준:

- 페이지 로드 시 학습기록 목록과 요약이 표시된다.
- 등록 성공 후 폼이 초기화되고 목록과 요약이 갱신된다.
- 수정 버튼 클릭 시 기존 날짜, 학습시간, 메모가 입력 폼에 채워진다.
- 수정 저장 시 `PUT /api/data/{document_id}`가 호출된다.
- 삭제 성공 후 목록과 요약이 갱신된다.
- API 실패 시 사용자가 이해할 수 있는 오류 메시지가 표시된다.

### 7.5 단계 3. AI 채팅 및 대화 기록 연동

상태: 예정

구현 범위:

- [ ] `POST /api/chat`
- [ ] `GET /api/conversations`
- [ ] `GET /api/conversations/{document_id}`
- [ ] `DELETE /api/conversations/{document_id}`
- [ ] AI 질문 입력
- [ ] AI 답변 표시
- [ ] AI 응답 로딩 상태 표시
- [ ] 이전 대화 목록 표시
- [ ] 이전 대화 클릭 시 상세 조회 후 채팅창 복원
- [ ] 대화 기록 삭제

중요 규칙:

- AI 질문 전송 시 프론트엔드는 `POST /api/chat`만 호출한다.
- 질문 전송 후 `POST /api/conversations`를 추가 호출하지 않는다.
- 대화 저장은 백엔드의 `/api/chat` 처리 흐름에서 자동 수행한다.

완료 기준:

- 질문 한 번당 `POST /api/chat`이 한 번만 호출된다.
- `conversations` 문서가 중복 저장되지 않는다.
- AI 답변이 화면에 표시된다.
- 응답 후 이전 대화 목록이 갱신된다.
- 이전 대화 목록에 질문, 답변, 생성 시간이 표시된다.
- 이전 대화 클릭 시 `GET /api/conversations/{document_id}`를 호출하고 질문과 답변이 채팅창에 복원된다.
- 대화 삭제 후 목록이 갱신된다.

### 7.6 단계 4. UI 안정화 및 사용성 개선

상태: 예정

구현 범위:

- [ ] 빈 데이터 안내
- [ ] 버튼 비활성화
- [ ] 입력값 검증 보강
- [ ] 로딩 표시 개선
- [ ] 오류 메시지 개선
- [ ] 모바일 반응형 보완
- [ ] 날짜와 시간 표시 정리
- [ ] 접근성과 사용성 개선

완료 기준:

- API 실패 시 화면이 멈추지 않는다.
- 데이터가 없을 때 자연스러운 빈 상태 메시지가 표시된다.
- 등록, 수정, 삭제, 질문 전송 중 중복 클릭이 방지된다.
- 모바일과 데스크톱에서 주요 기능을 사용할 수 있다.

### 7.7 단계 5. 최종 검증, README, 제출물 정리

상태: 예정

구현 범위:

- [ ] README에서 React, TypeScript, Vite, npm 실행 안내 제거
- [ ] 기술 스택을 HTML, CSS, Vanilla JavaScript로 수정
- [ ] 프론트엔드 로컬 실행 방법을 정적 파일 실행 방식으로 수정
- [ ] Render 백엔드 URL 추가
- [ ] Vercel 프론트엔드 URL 추가
- [ ] Swagger URL 추가
- [ ] 제출용 스크린샷 추가
- [ ] `CHECKLIST.md` 최종 검증 결과 반영

완료 기준:

- README와 실제 구현이 일치한다.
- `CHECKLIST.md`의 프론트엔드, 배포, 제출물 항목을 검증할 수 있다.
- Render와 Vercel 배포 URL이 유효하다.
- 최종 통합 흐름인 학습시간 등록, 요약 확인, AI 질문, 이전 대화 불러오기가 동작한다.

## 8. 샘플 데이터 및 검증 데이터 준비

- [ ] 학습시간 시계열 샘플 데이터를 최소 100개 준비한다.
  - 작업 내용: 서로 다른 날짜의 `date`, 0보다 큰 `value`, 선택적 `memo`를 갖는 데이터를 준비한다.
  - 완료 기준: Firestore `data` 컬렉션에서 유효한 데이터 포인트가 100개 이상 조회된다.
- [ ] 요약 통계 검증용 기대값을 준비한다.
  - 완료 기준: 샘플 데이터 기준으로 개수, 합계, 평균, 최대, 최소, 최근 7일 합계, 최근 추세의 기대값을 계산해 API 응답과 비교할 수 있다.
- [ ] API와 Firestore 통합 검증을 수행한다.
  - 완료 기준: 데이터 CRUD 4개와 요약 API, AI 채팅 API, 대화 기록 저장·목록·상세·삭제 API가 `/docs` 또는 API 클라이언트에서 정상 동작한다.
- [ ] 예외 상황을 검증한다.
  - 완료 기준: 빈 데이터, 잘못된 입력, 존재하지 않는 문서 ID, 환경변수 누락, Firestore/OpenAI 호출 실패에서 서버가 중단되지 않고 명확한 오류를 반환한다.

## 9. README 및 제출 준비

- [x] 백엔드 mock 기반 자동 테스트를 구성한다.
  - 작업 내용: Chat, 학습시간 데이터, 대화 기록, Firestore 서비스, Firebase core, health/root 라우터를 실제 외부 호출 없이 검증한다.
  - 완료 기준: Python 3.12 로컬 환경에서 `python -m pytest tests -v` 실행 결과가 `57 passed`이며 실제 Firebase, Firestore, OpenAI 요청이 발생하지 않는다.
- [x] GitHub Actions 백엔드 CI를 구성한다.
  - 작업 내용: `.github/workflows/backend-tests.yml`에서 Python 3.12 의존성 설치, compileall, pytest를 실행한다.
  - 완료 기준: `main` 브랜치 push 및 `main` 대상 pull request에서 workflow가 시작되도록 설정되어 있고 로컬에서 동일 검증 명령이 통과한다.
- [x] GitHub Actions 원격 실행 결과를 확인한다.
  - 완료 기준: GitHub의 `Backend Tests` workflow가 Python 3.12에서 compileall과 전체 pytest를 실행해 `57 passed`로 성공 완료된다.
- [ ] 백엔드를 Render에 배포한다.
  - 완료 기준: 환경변수가 Render에 설정되고 배포 URL의 `GET /`, `/docs`, Firestore 연동, OpenAI 채팅이 정상 동작한다.
- [ ] 프론트엔드를 Vercel에 배포한다.
  - 완료 기준: Vercel 환경에서 Render API 주소를 사용하고 CORS 오류 없이 데이터 관리, 요약, AI 채팅, 대화 불러오기가 동작한다.
- [ ] README에 필수 문서를 작성한다.
  - 작업 내용: 서비스 소개, 기술 스택, 프론트엔드·백엔드 API·Swagger 배포 URL, 로컬 실행 방법, 최소 환경변수 목록, Render 무료 티어의 첫 요청 지연 또는 콜드 스타트 안내를 작성한다.
  - 완료 기준: 새 개발자가 README만으로 로컬 실행과 배포 서비스 접속 방법을 이해할 수 있고 실제 비밀값은 포함되지 않는다.
- [ ] 제출용 스크린샷 3종을 README에 포함한다.
  - 작업 내용: 데이터 요약과 질문·답변이 보이는 채팅 화면, CRUD 중 1개 동작이 보이는 데이터 관리 화면, 불러오기 동작이 보이는 대화 기록 화면을 촬영한다.
  - 완료 기준: 각 스크린샷에서 요구 기능의 실행 결과를 식별할 수 있고 README에서 이미지가 정상 표시된다.
- [ ] 최종 배포 및 문서 검증을 수행한다.
  - 완료 기준: Render와 Vercel URL, Swagger, 환경변수 안내, 필수 스크린샷이 모두 유효하며 PRD 성공 기준을 전부 점검했다.
