"""
WebSocket 메시지 처리 핸들러들
각 메시지 타입별 처리 로직을 담당
"""

import json
import base64
from datetime import datetime
import string
from fastapi import WebSocket

from streaming_session import StreamingSessionManager


# 전역 스트리밍 세션 매니저
streaming_manager = StreamingSessionManager()


async def send_error_message(websocket: WebSocket, message: str):
    """에러 메시지 전송"""
    try:
        error_response = {
            "type": "error",
            "message": message,
            "timestamp": datetime.now().isoformat()
        }
        await websocket.send_text(json.dumps(error_response))
    except Exception as e:
        print(f"에러 메시지 전송 실패: {str(e)}")


async def send_welcome_message(websocket: WebSocket, active_connections_count: int):
    """환영 메시지 전송"""
    try:
        welcome_message = {
            "type": "connection",
            "message": "WebSocket 연결이 성공했습니다. 오디오 데이터를 전송해주세요.",
            "timestamp": datetime.now().isoformat(),
            "connections": active_connections_count,
            "language": "ko-KR"
        }
        await websocket.send_text(json.dumps(welcome_message))
    except Exception as e:
        print(f"환영 메시지 전송 실패: {str(e)}")


async def cleanup_websocket_session(websocket: WebSocket):
    """WebSocket 연결 종료시 세션 정리"""
    try:
        await streaming_manager.stop_session_by_websocket(websocket)
    except Exception as e:
        print(f"세션 정리 중 오류: {str(e)}")


async def handle_text_message(websocket: WebSocket, message_data: string):
    """텍스트 메시지 처리 함수 (기존 에코 기능)"""
    try:
        client_message = message_data
        response = {
            "type": "echo",
            "message": f"echo: {client_message}",
            "timestamp": datetime.now().isoformat()
        }
        await websocket.send_text(json.dumps(response))
        print(f"echo: {client_message}")
        
    except Exception as e:
        await send_error_message(websocket, f"텍스트 메시지 처리 중 오류: {str(e)}")


async def handle_binary_message(websocket: WebSocket, binary_data: bytes):
    """바이너리 데이터 처리 (직접 오디오 데이터)"""
    try:
        print(f"바이너리 오디오 데이터 수신: {len(binary_data)} bytes")
        
        # 현재 활성 스트리밍 세션이 있는지 확인
        if streaming_manager.has_session(websocket):
            # 기존 스트리밍 세션에 오디오 청크 추가
            await streaming_manager.add_audio_chunk(websocket, binary_data)
            print(f"스트리밍 세션에 바이너리 청크 추가: {len(binary_data)} bytes")
            
        else:
            # 새 스트리밍 세션 시작하고 첫 번째 청크 추가
            session_id = await streaming_manager.start_session(websocket, "ko-KR")
            await streaming_manager.add_audio_chunk(websocket, binary_data)
            
            # 시작 알림 전송
            response = {
                "type": "binary_streaming_started",
                "session_id": session_id,
                "message": "바이너리 데이터로 실시간 음성 인식이 시작되었습니다",
                "timestamp": datetime.now().isoformat()
            }
            await websocket.send_text(json.dumps(response))
            print(f"바이너리 스트리밍 세션 시작: {session_id}")
            
    except Exception as e:
        await send_error_message(websocket, f"바이너리 데이터 처리 중 오류: {str(e)}")
        print(f"바이너리 데이터 처리 오류: {str(e)}")


# 모듈에서 스트리밍 매니저 인스턴스 노출
def get_streaming_manager() -> StreamingSessionManager:
    """스트리밍 매니저 인스턴스 반환"""
    return streaming_manager
