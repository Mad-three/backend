"""
백엔드 서버 설정 파일

이 파일에서 서버의 모든 설정을 관리합니다.
코드에서 하드코딩하지 않고 별도 파일로 관리하면:
1. 환경에 따라 설정을 쉽게 변경할 수 있음
2. 보안상 중요한 정보를 분리할 수 있음
3. 코드의 가독성이 향상됨
"""

import os
from dotenv import load_dotenv

# 환경 감지 및 .env 파일 로드
# Docker 환경에서는 docker-compose.yml의 env_file을 통해 환경변수가 이미 주입되므로
# load_dotenv()를 호출하지 않음
if not os.path.exists('/.dockerenv') and not os.getenv('DOCKER_CONTAINER'):
    # 로컬 개발 환경에서만 .env 파일 로드
    load_dotenv()
    print("로컬 환경: .env 파일 로드됨")
else:
    print("Docker 환경: 환경변수는 이미 주입됨")

# ============== 서버 기본 설정 ==============

# 서버가 바인딩될 IP 주소
# "0.0.0.0": 모든 네트워크 인터페이스에서 접속 허용 (외부에서도 접속 가능)
# "127.0.0.1": 로컬호스트에서만 접속 허용 (보안상 더 안전)
HOST = os.getenv("HOST", "0.0.0.0")

# 서버가 사용할 포트 번호
# 8000: FastAPI의 기본 포트
# 다른 애플리케이션과 포트 충돌이 발생하면 변경 가능 (예: 8001, 8080 등)
PORT = int(os.getenv("PORT", "8000"))

# 개발 모드 설정
# True: 코드 변경 시 서버가 자동으로 재시작됨 (개발 시 편리)
# False: 수동으로 서버를 재시작해야 함 (프로덕션에서는 False 권장)
RELOAD = os.getenv("RELOAD", "true").lower() == "true"

# ============== CORS (Cross-Origin Resource Sharing) 설정 ==============

# 브라우저의 보안 정책상, 웹페이지가 다른 도메인의 서버에 요청을 보내는 것이 제한됨
# CORS 설정을 통해 특정 도메인에서의 접근을 허용할 수 있음

ALLOWED_ORIGINS = [
    # React 개발 서버의 기본 주소들
    "http://localhost:3000",      # React (Create React App) 기본 포트
    "http://127.0.0.1:3000",      # 위와 동일하지만 다른 형태의 로컬호스트 주소
    
    # Vite (최신 React 개발 도구) 기본 주소들
    "http://localhost:5173",      # Vite 기본 포트
    "http://127.0.0.1:5173",      # 위와 동일하지만 다른 형태의 로컬호스트 주소
    
    # 필요에 따라 추가 도메인을 여기에 추가
    # "https://myapp.com",        # 실제 배포된 프론트엔드 주소
]

# ============== 로깅 설정 ==============

# 서버 로그 출력 레벨
# "debug": 모든 디버그 정보 출력 (개발 시 유용)
# "info": 일반적인 정보 출력 (기본값)
# "warning": 경고 이상만 출력
# "error": 에러만 출력
LOG_LEVEL = os.getenv("LOG_LEVEL", "info")

# ============== Google Cloud 설정 ==============

# Google 서비스 계정 키 파일 경로
GOOGLE_APPLICATION_CREDENTIALS = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
