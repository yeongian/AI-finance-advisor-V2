@echo off
chcp 65001 >nul
echo.
echo ========================================
echo   AI 재무관리 어드바이저 - 간단 버전
echo ========================================
echo.
echo 🚀 API 서버 없이 내장 로직으로 실행합니다...
echo.

REM 현재 디렉토리로 이동
cd /d "%~dp0"

REM Python 환경 확인
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python이 설치되지 않았습니다.
    echo Python을 설치한 후 다시 시도해주세요.
    pause
    exit /b 1
)

REM 필수 패키지만 설치 (최소 의존성)
echo 📦 필수 패키지를 설치합니다...
pip install streamlit pandas numpy plotly python-dotenv

REM 로그 디렉토리 생성
if not exist "logs" mkdir logs

REM 간단 버전 시작
echo.
echo 🎯 간단 버전 시작...
echo 📱 브라우저에서 http://localhost:8502 을 열어주세요
echo.
echo 💡 이 버전은 API 서버나 외부 의존성 없이 내장 로직으로 동작합니다.
echo.

streamlit run main_simple.py --server.port 8502 --server.address 0.0.0.0

pause
