"""
실시간 음성 인식 스트리밍 세션 관리
Google Cloud Speech-to-Text API를 사용한 실시간 음성 인식 처리
"""

import asyncio
import json
import threading
import queue
from datetime import datetime
from typing import Optional
from fastapi import WebSocket
from google.cloud import speech


class StreamingSession:
    """실시간 음성 인식 스트리밍 세션"""
    
    def __init__(self, websocket: WebSocket, language_code: str = "ko-KR"):
        self.websocket = websocket
        self.language_code = language_code
        self.is_active = False
        self.streaming_config = None
        self.responses_task: Optional[asyncio.Task] = None
        self._audio_queue: Optional[asyncio.Queue] = None
        self._sync_audio_queue: Optional[queue.Queue] = None  # 동기 큐 추가
        self._speech_client = speech.SpeechClient()
        
    async def start_streaming(self):
        """스트리밍 세션 시작"""
        try:
            # Google STT 스트리밍 설정
            config = speech.RecognitionConfig(
                encoding=speech.RecognitionConfig.AudioEncoding.WEBM_OPUS,
                sample_rate_hertz=48000,
                language_code=self.language_code,
                enable_automatic_punctuation=True,
                model="latest_short",  # 실시간 처리에 최적화된 모델
            )
            
            self.streaming_config = speech.StreamingRecognitionConfig(
                config=config,
                interim_results=True,  # 중간 결과도 반환
                single_utterance=False,  # 연속 음성 인식
            )
            
            self.is_active = True
            print(f"스트리밍 세션 시작: {self.language_code}")
            
        except Exception as e:
            print(f"스트리밍 시작 오류: {str(e)}")
            await self._send_error(f"스트리밍 시작 실패: {str(e)}")
    
    async def add_audio_chunk(self, audio_data: bytes):
        """오디오 청크 추가"""
        if not self.is_active:
            await self.start_streaming()
        
        try:
            # 실시간으로 오디오 청크를 Google STT로 전송
            if self._audio_queue is None:
                # 첫 번째 청크인 경우 큐 생성 및 스트리밍 시작
                self._audio_queue = asyncio.Queue()
                self._sync_audio_queue = queue.Queue()  # 동기 큐도 생성
                await self._audio_queue.put(audio_data)
                self._sync_audio_queue.put(audio_data)
                
                # 스트리밍 요청 생성 및 시작
                await self._start_recognition_stream()
            else:
                await self._audio_queue.put(audio_data)
                self._sync_audio_queue.put(audio_data)
                
        except Exception as e:
            print(f"오디오 청크 처리 오류: {str(e)}")
            await self._send_error(f"오디오 처리 실패: {str(e)}")
    
    async def _start_recognition_stream(self):
        """Google STT 스트리밍 인식 시작"""
        try:
            # Google STT 스트리밍 인식 시작 (별도 태스크에서 실행)
            self.responses_task = asyncio.create_task(
                self._process_recognition_responses()
            )
            
        except Exception as e:
            print(f"스트리밍 인식 오류: {str(e)}")
            await self._send_error(f"음성 인식 실패: {str(e)}")
    
    async def _process_recognition_responses(self):
        """Google STT 응답 처리"""
        try:
            # 동기 오디오 생성기 생성
            def sync_audio_generator():
                """동기 오디오 생성기 (Google STT API용)"""
                while self.is_active and self._sync_audio_queue is not None:
                    try:
                        # 동기 큐에서 데이터 가져오기 (타임아웃 설정)
                        chunk = self._sync_audio_queue.get(timeout=1.0)
                        yield speech.StreamingRecognizeRequest(audio_content=chunk)
                    except queue.Empty:
                        # 타임아웃시 계속 대기
                        continue
                    except Exception as e:
                        print(f"동기 생성기 오류: {str(e)}")
                        break
            
            # Google STT 스트리밍 인식을 스레드풀에서 실행 (동기 함수)
            loop = asyncio.get_event_loop()
            responses = await loop.run_in_executor(
                None, 
                lambda: self._speech_client.streaming_recognize(
                    self.streaming_config, sync_audio_generator()
                )
            )
            
            # 응답 처리
            await self._process_streaming_responses(responses)
            
        except Exception as e:
            print(f"인식 응답 처리 오류: {str(e)}")
            await self._send_error(f"음성 인식 응답 처리 실패: {str(e)}")
    
    async def _generate_audio_chunks(self):
        """오디오 청크 생성기"""
        while self.is_active and self._audio_queue is not None:
            try:
                # 큐에서 오디오 청크 가져오기 (타임아웃 설정)
                chunk = await asyncio.wait_for(
                    self._audio_queue.get(), timeout=1.0
                )
                yield chunk
            except asyncio.TimeoutError:
                # 타임아웃시 계속 대기
                continue
            except Exception as e:
                print(f"오디오 생성기 오류: {str(e)}")
                break
    
    async def _process_streaming_responses(self, responses):
        """스트리밍 응답 처리"""
        try:
            for response in responses:
                if not self.is_active:
                    break
                
                for result in response.results:
                    if result.alternatives:
                        transcript = result.alternatives[0].transcript
                        confidence = result.alternatives[0].confidence
                        is_final = result.is_final
                        
                        # 실시간 결과 전송
                        await self._send_transcript(
                            transcript, confidence, is_final
                        )
                        
                        if is_final:
                            print(f"최종 결과: {transcript} (신뢰도: {confidence:.2f})")
                        else:
                            print(f"중간 결과: {transcript}")
                            
        except Exception as e:
            print(f"응답 처리 오류: {str(e)}")
            await self._send_error(f"응답 처리 실패: {str(e)}")
    
    async def _send_transcript(self, transcript: str, confidence: float, is_final: bool):
        """음성 인식 결과 전송"""
        try:
            response = {
                "type": "streaming_transcription",
                "message": transcript,
                "confidence": confidence,
                "is_final": is_final,
                "language": self.language_code,
                "timestamp": datetime.now().isoformat()
            }
            await self.websocket.send_text(json.dumps(response))
            
        except Exception as e:
            print(f"결과 전송 오류: {str(e)}")
    
    async def _send_error(self, message: str):
        """에러 메시지 전송"""
        try:
            error_response = {
                "type": "streaming_error",
                "message": message,
                "timestamp": datetime.now().isoformat()
            }
            await self.websocket.send_text(json.dumps(error_response))
        except Exception as e:
            print(f"에러 메시지 전송 실패: {str(e)}")
    
    async def stop_streaming(self):
        """스트리밍 세션 중지"""
        self.is_active = False
        
        if self.responses_task and not self.responses_task.done():
            self.responses_task.cancel()
            try:
                await self.responses_task
            except asyncio.CancelledError:
                pass
        
        # 큐 정리
        if self._audio_queue:
            while not self._audio_queue.empty():
                try:
                    self._audio_queue.get_nowait()
                except:
                    break
            self._audio_queue = None
        
        # 동기 큐 정리
        if self._sync_audio_queue:
            while not self._sync_audio_queue.empty():
                try:
                    self._sync_audio_queue.get_nowait()
                except:
                    break
            self._sync_audio_queue = None
            
        print("스트리밍 세션 중지")


class StreamingSessionManager:
    """스트리밍 세션 관리자"""
    
    def __init__(self):
        self.sessions = {}
    
    def get_session_id(self, websocket: WebSocket) -> int:
        """WebSocket 객체의 고유 ID 반환"""
        return id(websocket)
    
    async def start_session(self, websocket: WebSocket, language: str = "ko-KR") -> str:
        """새 스트리밍 세션 시작"""
        session_id = self.get_session_id(websocket)
        
        # 기존 세션이 있다면 중지
        if session_id in self.sessions:
            await self.stop_session(session_id)
        
        # 새 세션 생성
        self.sessions[session_id] = StreamingSession(websocket, language)
        await self.sessions[session_id].start_streaming()
        
        print(f"스트리밍 세션 시작: {session_id}")
        return str(session_id)
    
    async def add_audio_chunk(self, websocket: WebSocket, audio_data: bytes):
        """오디오 청크를 세션에 추가"""
        session_id = self.get_session_id(websocket)
        
        if session_id not in self.sessions:
            raise ValueError("스트리밍 세션이 시작되지 않았습니다")
        
        await self.sessions[session_id].add_audio_chunk(audio_data)
    
    async def stop_session(self, session_id: int):
        """스트리밍 세션 중지"""
        if session_id in self.sessions:
            await self.sessions[session_id].stop_streaming()
            del self.sessions[session_id]
            print(f"스트리밍 세션 중지: {session_id}")
    
    async def stop_session_by_websocket(self, websocket: WebSocket):
        """WebSocket으로 세션 중지"""
        session_id = self.get_session_id(websocket)
        await self.stop_session(session_id)
    
    def has_session(self, websocket: WebSocket) -> bool:
        """세션 존재 여부 확인"""
        session_id = self.get_session_id(websocket)
        return session_id in self.sessions
    
    async def cleanup_all_sessions(self):
        """모든 세션 정리"""
        session_ids = list(self.sessions.keys())
        for session_id in session_ids:
            await self.stop_session(session_id)
