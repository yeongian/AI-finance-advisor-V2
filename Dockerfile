# AI 재무관리 어드바이저 Docker 이미지
FROM python:3.11-slim

# 작업 디렉토리 설정
WORKDIR /app

# 시스템 패키지 업데이트 및 필요한 패키지 설치
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Python 의존성 파일 복사
COPY requirements.txt .

# Python 패키지 설치
RUN pip install --no-cache-dir -r requirements.txt

# 애플리케이션 코드 복사
COPY . .

# 데이터 디렉토리 생성
RUN mkdir -p data/vector_store

# 포트 노출
EXPOSE 8000 8501

# 환경변수 설정
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# 헬스체크
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# 실행 스크립트 복사
COPY docker-entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

# 진입점 설정
ENTRYPOINT ["docker-entrypoint.sh"]
