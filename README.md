# PresentationAngel Backend

FastAPI + WebSocket을 사용한 실시간 음성 인식 백엔드 서버입니다.

## 🎯 프로젝트 목표
WebSocket을 통해 실시간으로 오디오 데이터를 받아 Google STT API로 음성 인식 처리를 수행합니다.
- 프론트엔드: React + WebSocket 클라이언트
- 백엔드: FastAPI + WebSocket + Google Cloud Speech-to-Text API

## 📁 프로젝트 구조
```
backend/
├── main.py                 # FastAPI 메인 애플리케이션
├── config.py              # 환경 설정 관리
├── streaming_session.py   # 실시간 스트리밍 세션 관리
├── audio_utils.py         # 오디오 처리 유틸리티
├── websocket_handlers.py  # WebSocket 메시지 핸들러
├── requirements.txt       # Python 종속성
├── Dockerfile            # Docker 컨테이너 설정
├── docker-compose.yml    # Docker Compose 설정
├── .env                  # 로컬 환경 변수
├── .env.docker          # Docker 환경 변수
└── API_DOCS_FOR_FRONTEND.md  # 프론트엔드 개발자용 API 문서
```

## 🔧 모듈 설명

### main.py
- FastAPI 애플리케이션 진입점
- WebSocket 엔드포인트 정의
- CORS 미들웨어 설정
- 서버 실행 설정

### streaming_session.py
- `StreamingSession`: 실시간 음성 인식 세션 클래스
- `StreamingSessionManager`: 다중 세션 관리
- Google STT API 스트리밍 처리 로직

### websocket_handlers.py
- WebSocket 메시지 타입별 처리 함수
- 실시간 스트리밍 오디오 처리
- 단일 오디오 파일 처리
- 에러 메시지 처리

## 🚀 빠른 시작 (초보자용)

### 전제 조건
- Python 3.8 이상이 설치되어 있어야 합니다
- 터미널/명령 프롬프트 사용법을 알아야 합니다

### 1단계: 프로젝트 디렉토리로 이동
```bash
# Windows PowerShell
cd C:\your-project-path\PresentationAngel\backend

# 또는 상대 경로로
cd backend
```

### 2단계: Python 가상환경 생성 (권장)
```bash
# 가상환경 생성
python -m venv venv

# 가상환경 활성화 (Windows)
venv\Scripts\activate

# 가상환경 활성화 (Mac/Linux)
source venv/bin/activate
```

### 3단계: 필요한 패키지 설치
```bash
pip install -r requirements.txt
```

설치되는 패키지들:
- `fastapi`: 웹 API 프레임워크
- `uvicorn`: ASGI 서버 (FastAPI 실행용)
- `websockets`: WebSocket 통신 지원
- `python-multipart`: 파일 업로드 지원

### 4단계: 서버 실행
```bash
python main.py
```

성공하면 다음과 같은 메시지가 출력됩니다:
```
INFO:     Started server process [12345]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

### 5단계: 서버 동작 확인
1. **웹 브라우저**에서 `http://localhost:8000` 접속
   - 서버 상태 메시지가 표시되어야 함

2. **서버 상태 확인**: `http://localhost:8000/health`
   - JSON 형태의 서버 정보가 표시되어야 함

## 🔧 상세 설명

### WebSocket 통신 흐름
1. **클라이언트 연결**: `ws://localhost:8000/ws`로 WebSocket 연결
2. **연결 성공 메시지**: 서버가 연결 확인 메시지 전송
3. **메시지 송수신**: 
   - 클라이언트가 JSON 메시지 전송: `{"message": "Hello, World"}`
   - 서버가 에코 응답: `{"echo": "Hello, World", "timestamp": "..."}`

### 메시지 형식

**클라이언트 → 서버**
```json
{
  "message": "Hello, World"
}
```

**서버 → 클라이언트**
```json
{
  "echo": "Hello, World",
  "timestamp": "2024-01-01T12:00:00.000000"
}
```

## 📁 프로젝트 구조
```
backend/
├── main.py           # 메인 서버 파일 (FastAPI 앱 정의)
├── config.py         # 서버 설정 (포트, CORS 등)
├── requirements.txt  # Python 패키지 의존성
└── README.md        # 이 파일 (사용법 설명)
```

### 각 파일의 역할
- **main.py**: FastAPI 서버의 핵심 로직, WebSocket 처리
- **config.py**: 서버 설정값들 (포트 번호, CORS 설정 등)
- **requirements.txt**: 프로젝트에서 사용하는 Python 패키지 목록

## ⚙️ 설정 변경

### 포트 번호 변경
`config.py` 파일에서 `PORT` 값을 수정:
```python
PORT = 8001  # 8000 대신 8001 포트 사용
```

### CORS 설정 (프론트엔드 주소 추가)
`config.py` 파일의 `ALLOWED_ORIGINS`에 프론트엔드 주소 추가:
```python
ALLOWED_ORIGINS = [
    "http://localhost:3000",    # 기존 React 주소
    "http://your-new-domain.com"  # 새로 추가할 주소
]
```

## 🐛 문제 해결

### 포트가 이미 사용 중인 경우
```
OSError: [WinError 10048] 각 소켓 주소에 대해 하나의 사용이 일반적으로 허용됩니다
```
**해결책**: `config.py`에서 다른 포트 번호로 변경 (예: 8001, 8080)

### 패키지 설치 실패
```
pip install -r requirements.txt
```
**해결책**: 
1. Python 버전 확인: `python --version` (3.8 이상 필요)
2. pip 업그레이드: `pip install --upgrade pip`

### 서버 실행 실패
**해결책**: 
1. 가상환경이 활성화되어 있는지 확인
2. 필요한 패키지가 모두 설치되어 있는지 확인

## 🔄 개발 모드
서버는 자동 재시작 모드로 실행됩니다. 코드를 수정하면 자동으로 서버가 재시작됩니다.

서버 중지: `Ctrl + C` 

{
    "type": "audio" | "text"
}