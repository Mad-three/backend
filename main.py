"""
PresentationAngel Backend Server
FastAPI + WebSocket을 사용한 백엔드 서버

주요 기능:
1. WebSocket을 통한 실시간 통신
2. 클라이언트가 보낸 오디오 데이터를 Google STT API로 음성 인식
"""

# 필요한 라이브러리들을 가져오기 (import)
from fastapi import FastAPI, WebSocket, WebSocketDisconnect  # FastAPI 웹 프레임워크
from fastapi.middleware.cors import CORSMiddleware           # 브라우저 보안 정책(CORS) 처리
import uvicorn                                              # ASGI 서버 (FastAPI 실행용)
from datetime import datetime                               # 시간 정보 처리

import config  # 우리가 만든 설정 파일

# 분리된 모듈들 import
from websocket_handlers import (
    handle_text_message, 
    handle_binary_message,
    send_welcome_message,
    send_error_message,
    cleanup_websocket_session,
)
from auth import router as auth_router

# FastAPI 애플리케이션 인스턴스 생성
# title: API 문서에 표시될 제목
# version: API 버전
app = FastAPI(title="PresentationAngel Backend", version="1.0.0")

app.include_router(auth_router, prefix="/auth")

# CORS(Cross-Origin Resource Sharing) 미들웨어 설정
# 브라우저가 다른 도메인의 서버에 요청을 보낼 수 있도록 허용
# 예: 프론트엔드(localhost:3000)가 백엔드(localhost:8000)에 접근 가능하게 함
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.ALLOWED_ORIGINS,  # 허용할 도메인 목록 (config.py에서 정의)
    allow_credentials=True,                # 쿠키, 인증 정보 포함 요청 허용
    allow_methods=["*"],                   # 모든 HTTP 메서드 허용 (GET, POST, etc.)
    allow_headers=["*"],                   # 모든 HTTP 헤더 허용
)

# 현재 연결된 WebSocket 클라이언트들을 저장하는 리스트
# 나중에 여러 클라이언트가 동시에 연결될 때 관리하기 위함
active_connections = []

@app.get("/")
async def root():
    """
    루트 경로 엔드포인트 (GET /)
    
    용도: 서버가 정상적으로 실행되고 있는지 확인
    응답: JSON 형태의 서버 상태 정보
    
    브라우저에서 http://localhost:8000/ 로 접속하면 이 함수가 실행됨
    """
    return {"message": "PresentationAngel Backend Server", "status": "running"}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket 연결 처리 함수 (ws://localhost:8000/ws)
    
    WebSocket이란?
    - HTTP와 달리 서버와 클라이언트가 실시간으로 양방향 통신할 수 있는 기술
    - 한 번 연결되면 계속 연결 상태를 유지하며 메시지를 주고받을 수 있음
    
    이 함수의 역할:
    1. 클라이언트의 WebSocket 연결 요청을 받아들임
    2. 연결 성공 메시지를 클라이언트에게 전송
    3. 클라이언트가 보내는 오디오 데이터를 기다림
    4. 받은 오디오 데이터를 Google STT API로 처리하여 텍스트 반환
    """
    
    # 1단계: WebSocket 연결 요청을 수락
    await websocket.accept()
    
    # 2단계: 연결된 클라이언트를 관리 리스트에 추가
    active_connections.append(websocket)
    
    try:
        # 3단계: 클라이언트에게 연결 성공 알림 메시지 전송
        await send_welcome_message(websocket, len(active_connections))
        print(f"새 클라이언트 연결됨. 총 연결 수: {len(active_connections)}")
        
        # 4단계: 무한 루프로 클라이언트 메시지 대기
        while True:
            # 클라이언트로부터 텍스트 메시지 수신 (대기 상태)
            message = await websocket.receive()
            
            try:
                if message["type"] == "websocket.receive":
                    if "text" in message:
                        # 텍스트 메시지 처리
                        await handle_text_message(websocket, message["text"])
                    elif "bytes" in message:
                        # 바이너리 데이터 처리
                        await handle_binary_message(websocket, message["bytes"])
                    else:
                        # 알 수 없는 메시지 타입
                        await send_error_message(websocket, "알 수 없는 메시지 타입입니다.")
                else:
                    # 알 수 없는 메시지 타입
                    await send_error_message(websocket, "알 수 없는 메시지 타입입니다.")
            
            except Exception as e:
                # 예상치 못한 에러가 발생한 경우
                await send_error_message(websocket, f"메시지 처리 중 오류: {str(e)}")
                print(f"메시지 처리 오류: {str(e)}")
                
    except WebSocketDisconnect:
        # 클라이언트가 연결을 끊었을 때 처리
        await cleanup_websocket_session(websocket)
        
        # 연결 목록에서 제거
        if websocket in active_connections:
            active_connections.remove(websocket)
        print(f"클라이언트 연결 해제. 남은 연결: {len(active_connections)}")

@app.get("/health")
async def health_check():
    """
    서버 헬스 체크 엔드포인트 (GET /health)
    
    용도: 서버가 정상 작동하는지 확인하고 현재 상태 정보 제공
    응답: 서버 상태, 현재 WebSocket 연결 수, 현재 시간
    
    모니터링 도구나 로드밸런서에서 서버 상태를 확인할 때 사용
    """
    return {
        "status": "healthy",                               # 서버 상태
        "active_connections": len(active_connections),     # 현재 활성 WebSocket 연결 수
        "timestamp": datetime.now().isoformat()           # 현재 시간
    }

# 이 파일이 직접 실행될 때만 서버 시작 (python main.py로 실행할 때)
# 다른 파일에서 import할 때는 실행되지 않음
if __name__ == "__main__":
    """
    서버 실행 설정
    
    uvicorn: FastAPI 애플리케이션을 실행하는 ASGI 서버
    - "main:app": main.py 파일의 app 객체를 실행
    - host: 접속 가능한 IP 주소 (0.0.0.0은 모든 IP에서 접속 가능)
    - port: 서버 포트 번호
    - reload: 코드 변경 시 자동 재시작 (개발 시에만 사용)
    - log_level: 로그 출력 레벨
    """
    uvicorn.run(
        "main:app",                # 실행할 FastAPI 앱
        host=config.HOST,          # 서버 호스트 (config.py에서 설정)
        port=config.PORT,          # 서버 포트 (config.py에서 설정)
        reload=config.RELOAD,      # 자동 재시작 여부 (config.py에서 설정)
        log_level=config.LOG_LEVEL # 로그 레벨 (config.py에서 설정)
    ) 