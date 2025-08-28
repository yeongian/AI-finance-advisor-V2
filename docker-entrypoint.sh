#!/bin/bash

# AI 재무관리 어드바이저 Docker 실행 스크립트

echo "🚀 AI 재무관리 어드바이저 시작 중..."

# 환경변수 확인
if [ -z "$AOAI_API_KEY" ]; then
    echo "❌ AOAI_API_KEY 환경변수가 설정되지 않았습니다."
    exit 1
fi

# 데이터 디렉토리 확인
if [ ! -d "/app/data" ]; then
    mkdir -p /app/data
fi

# 벡터 스토어 디렉토리 확인
if [ ! -d "/app/data/vector_store" ]; then
    mkdir -p /app/data/vector_store
fi

# API 서버 시작 (백그라운드)
echo "📍 API 서버 시작 중..."
uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload &
API_PID=$!

# 잠시 대기
sleep 5

# Streamlit 서버 시작 (백그라운드)
echo "🌐 Streamlit 서버 시작 중..."
streamlit run simple_streamlit_app.py --server.port 8501 --server.address 0.0.0.0 &
STREAMLIT_PID=$!

echo "✅ 모든 서버가 시작되었습니다!"
echo "📍 API 서버: http://localhost:8000"
echo "🌐 웹 인터페이스: http://localhost:8501"

# 프로세스 모니터링
wait $API_PID $STREAMLIT_PID
