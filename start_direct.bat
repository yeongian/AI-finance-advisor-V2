@echo off
chcp 65001 >nul
echo.
echo ========================================
echo   AI 재무관리 어드바이저 - 직접 실행 모드
echo ========================================
echo.
echo 🚀 API 서버 없이 직접 실행합니다...
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

REM 필요한 패키지 설치 확인
echo 📦 필요한 패키지를 확인하고 설치합니다...
pip install -r requirements.txt

REM 로그 디렉토리 생성
if not exist "logs" mkdir logs

REM 직접 실행 모드 시작
echo.
echo 🎯 직접 실행 모드 시작...
echo 📱 브라우저에서 http://localhost:8501 을 열어주세요
echo.
echo 💡 이 모드는 API 서버 없이 모든 기능을 직접 실행합니다.
echo.

streamlit run main_direct.py --server.port 8501 --server.address 0.0.0.0

pause
