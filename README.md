# AI 학습시간 분석 비서

학습시간 시계열 데이터를 분석하고 AI 학습 조언을 제공하는 웹서비스 프로젝트입니다.

## 기술 스택

- Backend: Python, FastAPI, Uvicorn
- Database: Firebase Firestore
- AI: OpenAI API
- Frontend: HTML, CSS, Vanilla JavaScript

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

## 환경변수 준비

루트의 `.env.example`을 참고하여 다음 환경변수를 로컬 `.env`에 설정합니다.

- `OPENAI_API_KEY`
- `FIREBASE_PROJECT_ID`
- `FIREBASE_CLIENT_EMAIL`
- `FIREBASE_PRIVATE_KEY`
- `FRONTEND_ORIGIN`

실제 OpenAI API 키, Firebase 개인키, 서비스 계정 JSON 등 비밀값은 README나 Git에 커밋하지 마세요.

## Render Python 버전

Render에서도 로컬 검증 환경과 같은 Python 3.12를 선택하고 배포 로그에서 실제 버전을 확인합니다. Render 서비스 루트가 아직 확정되지 않았으므로 `runtime.txt`는 추가하지 않았습니다.

서비스 루트가 저장소 루트인지 `backend`인지 확정한 뒤 해당 루트 기준으로 Python 3.12 런타임 설정을 적용합니다.


## 임시

swagger 주소 : http://127.0.0.1:8000/docs

FastASPI : 127.0.0.1:8000/docs
  API원본 문서 : http://127.0.0.1:8000/openapi.json

 목적	         주소
기본 API 확인	http://127.0.0.1:8000/
Swagger UI	http://127.0.0.1:8000/docs
OpenAPI JSON	http://127.0.0.1:8000/openapi.jso


## FIREBASE
