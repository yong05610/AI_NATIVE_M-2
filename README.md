# AI 학습시간 분석 비서

학습시간 시계열 데이터를 기록·분석하고 저장된 학습 이력을 바탕으로 AI 학습 조언을 제공하는 웹서비스입니다. React 화면에서 학습시간과 대화를 관리하고, FastAPI와 Firestore에 데이터를 저장하며 OpenAI API로 한국어 학습 코칭 답변을 생성합니다.

## 주요 기능

- 학습시간 데이터 생성, 목록 조회, 수정, 삭제
- 전체 및 최근 7일 학습시간 통계와 최근 추세 요약
- 질문·답변 1쌍 단위 대화 기록 저장, 목록·상세 조회, 삭제
- 최근 학습시간 데이터 최대 10개와 요약 통계를 활용한 OpenAI 채팅 응답
- AI 답변 생성 후 `conversations` 컬렉션에 질문과 답변 자동 저장
- Firestore 연결 상태 확인
- Firebase, Firestore, OpenAI를 실제 호출하지 않는 pytest 자동 테스트
- GitHub Actions 기반 compileall 및 pytest 자동 검증

## 기술 스택

- Backend: Python, FastAPI, Uvicorn
- Database: Firebase Firestore
- AI: OpenAI API
- Frontend: React, TypeScript, Vite, CSS

## 프론트엔드 로컬 실행

백엔드를 먼저 `http://127.0.0.1:8000`에서 실행한 뒤 별도 PowerShell에서 프론트엔드를 시작합니다.

```powershell
cd frontend
npm install
npm run dev
```

기본 접속 주소는 `http://localhost:5173`입니다. 개발 중에는 Vite 프록시가 `/api` 요청을 로컬 백엔드로 전달합니다. 배포 환경이나 별도 백엔드 주소를 사용할 때는 `frontend/.env.example`을 참고해 다음 변수만 설정합니다.

```text
VITE_API_BASE_URL=http://localhost:8000
```

프론트엔드 프로덕션 빌드는 `frontend` 디렉터리에서 `npm run build`로 확인합니다. 실제 API 키나 Firebase 인증정보는 프론트엔드 코드 또는 환경변수에 넣지 않습니다.

## API 엔드포인트

| 메서드 | 경로 | 기능 |
| --- | --- | --- |
| `GET` | `/` | API 기본 상태 확인 |
| `GET` | `/api/health/firestore` | Firestore 연결 상태 확인 |
| `POST` | `/api/chat` | 학습 데이터 기반 AI 답변 생성 및 대화 자동 저장 |
| `POST` | `/api/conversations` | 질문·답변 대화 기록 저장 |
| `GET` | `/api/conversations` | 대화 기록 목록 조회 |
| `GET` | `/api/conversations/{document_id}` | 특정 대화 기록 조회 |
| `DELETE` | `/api/conversations/{document_id}` | 특정 대화 기록 삭제 |
| `POST` | `/api/data` | 학습시간 데이터 생성 |
| `GET` | `/api/data` | 학습시간 데이터 목록 조회 |
| `PUT` | `/api/data/{document_id}` | 학습시간 데이터 수정 |
| `DELETE` | `/api/data/{document_id}` | 학습시간 데이터 삭제 |
| `GET` | `/api/data/summary` | 학습시간 요약 통계 조회 |

## Python 버전 정책

- 권장 및 로컬 검증: Python 3.12.x
- 허용: Python 3.11 이상(단, Python 3.14 제외)
- 비권장·검증 제외: Python 3.14

시스템의 기본 Python이 3.14여도 이 프로젝트 실행에는 사용하지 않습니다. 모든 로컬 명령은 프로젝트 루트의 `.venv`를 활성화한 상태에서 실행합니다.

## Windows PowerShell 로컬 실행

프로젝트 루트에서 Python 3.12 기반 가상환경을 만들고 활성화합니다.

```powershell
# 프로젝트 루트에서 실행
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1

python --version
python -m pip --version
python -m pip install --upgrade pip
python -m pip install -r backend/requirements.txt

cd backend
python -m uvicorn main:app --reload
```

실행 후 기본 상태 API는 `http://127.0.0.1:8000/`, Swagger UI는 `http://127.0.0.1:8000/docs`에서 확인할 수 있습니다.

PowerShell 실행 정책 때문에 가상환경 활성화가 차단되면 다음 명령을 한 번 실행한 뒤 다시 활성화합니다.

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

## macOS/Linux 보조 명령

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python --version
python -m pip install --upgrade pip
python -m pip install -r backend/requirements.txt
cd backend
python -m uvicorn main:app --reload
```

## 실행 보조 스크립트

Windows PowerShell에서는 프로젝트 루트에서 다음 스크립트를 사용할 수 있습니다.

```powershell
.\scripts\setup_venv.ps1
.\scripts\run_backend.ps1
```

## 테스트

프로젝트 루트에서 문법 검사를 실행합니다.

```powershell
.\.venv\Scripts\python.exe -m compileall -q backend
```

전체 백엔드 테스트는 다음과 같이 실행합니다.

```powershell
cd backend
..\.venv\Scripts\python.exe -m pytest tests -v
```

현재 로컬 검증 결과는 `57 passed, 1 warning`입니다. 테스트에서는 Firebase Admin SDK, Firestore, OpenAI 호출을 mock 처리하므로 실제 외부 API 요청이나 DB 변경이 발생하지 않습니다.

## GitHub Actions CI

- Workflow: `.github/workflows/backend-tests.yml`
- Python: 3.12
- 실행 조건: `main` 브랜치 push, `main` 대상 pull request
- 실행 단계: 의존성 설치, `python -m compileall -q backend`, 전체 pytest
- 원격 실행 결과: `Backend Tests` workflow 성공, `57 passed`

로컬과 GitHub Actions에서 동일한 compileall 및 pytest 검증이 통과했습니다. 저장소 소유자와 이름이 확정되지 않아 CI 상태 배지는 추가하지 않았습니다.

## 환경변수 준비

루트의 `.env.example`을 참고하여 다음 환경변수를 로컬 `.env`에 설정합니다.

- `OPENAI_API_KEY`
- `OPENAI_MODEL` — 선택 사항, 기본값 `gpt-4o-mini`
- `FIREBASE_PROJECT_ID`
- `FIREBASE_CLIENT_EMAIL`
- `FIREBASE_PRIVATE_KEY`
- `FRONTEND_ORIGIN`

실제 OpenAI API 키, Firebase 개인키, 서비스 계정 JSON 등 비밀값은 README나 Git에 커밋하지 마세요.

`.env.example`에는 예시 값만 유지하고 실제 값은 로컬 `.env` 또는 배포 서비스의 환경변수 설정으로 주입합니다.

## Render Python 버전

Render에서도 로컬 검증 환경과 같은 Python 3.12를 선택하고 배포 로그에서 실제 버전을 확인합니다. Render 서비스 루트가 아직 확정되지 않았으므로 `runtime.txt`는 추가하지 않았습니다.

서비스 루트가 저장소 루트인지 `backend`인지 확정한 뒤 해당 루트 기준으로 Python 3.12 런타임 설정을 적용합니다.

Render 무료 티어를 사용할 경우 서비스가 유휴 상태에서 중지되어 첫 요청 응답이 지연될 수 있습니다. 첫 요청에서 콜드 스타트가 발생하면 잠시 기다린 뒤 다시 확인하세요.

## 배포 상태

현재 README에는 확정된 Render 백엔드 URL과 Vercel 프론트엔드 URL이 없습니다. 배포가 완료되면 서비스 URL과 Swagger URL을 추가하고 실제 Firebase, Firestore, OpenAI 통합 동작을 별도로 검증해야 합니다.
