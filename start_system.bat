@echo off
chcp 65001 >nul
echo 🚀 AI 재무관리 어드바이저 전체 시스템 시작
echo ================================================

REM 환경 변수 설정
set AOAI_ENDPOINT=https://skcc-atl-dev-openai-01.openai.azure.com/
set AOAI_API_KEY=5kWBVPecvaqFeiB3PJYXnfkMHclg66duBhVXY5lWE9z187WonAnAJQQJ99BBACYeBjFXJ3w3AAABACOGqwfl
set AOAI_DEPLOY_GPT4O_MINI=gpt-4o-mini

echo ✅ 환경 변수 설정 완료

REM Python 경로 확인
py --version
if %errorlevel% neq 0 (
    echo ❌ Python이 설치되지 않았습니다.
    echo 💡 Python을 설치하거나 PATH를 확인해주세요.
    pause
    exit /b 1
)

echo ✅ Python 확인 완료

echo 🚀 API 서버 시작 중...
start "API Server" cmd /k "py -m uvicorn src.api.main:app --host localhost --port 8000 --reload"

echo ⏳ API 서버 시작 대기 중...
timeout /t 5 /nobreak >nul

echo 🌐 웹 인터페이스 시작 중...
start "Web Interface" cmd /k "py -m streamlit run main.py --server.port 8501"

echo ⏳ 웹 인터페이스 시작 대기 중...
timeout /t 3 /nobreak >nul

echo.
echo 🎉 시스템이 성공적으로 시작되었습니다!
echo ================================================
echo 📊 API 서버: http://localhost:8000
echo 🌐 웹 인터페이스: http://localhost:8501
echo 📚 API 문서: http://localhost:8000/docs
echo ================================================
echo 💡 종료하려면 각 창을 닫거나 Ctrl+C를 누르세요.
echo.

pause
