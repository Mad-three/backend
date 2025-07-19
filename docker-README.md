# 🐳 Docker 사용 가이드

## 필수 요구사항

- Docker 설치됨
- Docker Compose 설치됨

## 빠른 시작

### 1. Docker Compose로 실행 (권장)

```bash
# 이미지 빌드 및 컨테이너 실행
docker-compose up --build

# 백그라운드에서 실행
docker-compose up -d --build

# 로그 확인
docker-compose logs -f

# 중지
docker-compose down
```

### 2. Docker만 사용하는 경우

```bash
# 이미지 빌드
docker build -t presentation-angel-backend .

# 컨테이너 실행
docker run -d \
  --name presentation-angel-backend \
  -p 8000:8000 \
  -v $(pwd)/google-key.json:/app/google-key.json:ro \
  presentation-angel-backend

# 로그 확인
docker logs -f presentation-angel-backend

# 컨테이너 중지 및 삭제
docker stop presentation-angel-backend
docker rm presentation-angel-backend
```

## 접속 정보

- **API 서버**: http://localhost:8000
- **헬스체크**: http://localhost:8000/health
- **WebSocket**: ws://localhost:8000/ws

## 개발 모드

개발 중에 코드 변경사항을 실시간으로 반영하려면:

```bash
# docker-compose.yml에서 volumes 섹션이 활성화되어 있는지 확인
docker-compose up --build
```

코드를 수정하면 컨테이너 내부의 파일도 자동으로 업데이트됩니다.

## 유용한 명령어

```bash
# 컨테이너 내부 접속
docker-compose exec backend bash

# 이미지 삭제
docker rmi presentation-angel-backend

# 모든 컨테이너, 이미지, 볼륨 정리
docker system prune -a

# 특정 컨테이너의 리소스 사용량 확인
docker stats presentation-angel-backend
```

## 문제해결

### 포트 충돌
```bash
# 다른 포트로 실행
docker run -p 8001:8000 presentation-angel-backend
```

### 권한 문제
```bash
# 현재 사용자 권한으로 실행
docker run --user $(id -u):$(id -g) presentation-angel-backend
```

### 로그 레벨 변경
```bash
# 환경변수로 로그 레벨 설정
docker run -e LOG_LEVEL=debug presentation-angel-backend
```
