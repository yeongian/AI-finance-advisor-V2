@echo off
chcp 65001 >nul
echo ================================================
echo 🛑 AI 재무관리 어드바이저 - 모든 서버 중지
echo ================================================
echo.

echo [1/2] 서버 실행 상태 확인 및 종료...
echo 포트 8000 (API 서버) 확인 중...
netstat -an | findstr :8000 >nul 2>&1
if %errorlevel% equ 0 (
    echo ⚠️  포트 8000에서 실행 중인 서버를 발견했습니다. 종료 중...
    for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8000') do (
        taskkill /f /pid %%a >nul 2>&1
    )
    echo ✅ 포트 8000 프로세스 종료됨
) else (
    echo ✅ 포트 8000에서 실행 중인 서버가 없습니다.
)

echo 포트 8501 (Streamlit UI) 확인 중...
netstat -an | findstr :8501 >nul 2>&1
if %errorlevel% equ 0 (
    echo ⚠️  포트 8501에서 실행 중인 서버를 발견했습니다. 종료 중...
    for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8501') do (
        taskkill /f /pid %%a >nul 2>&1
    )
    echo ✅ 포트 8501 프로세스 종료됨
) else (
    echo ✅ 포트 8501에서 실행 중인 서버가 없습니다.
)

echo.
echo [2/2] Docker 컨테이너 상태 확인 및 종료...
docker ps | findstr ai-finance-advisor >nul 2>&1
if %errorlevel% equ 0 (
    echo ⚠️  실행 중인 Docker 컨테이너를 발견했습니다. 종료 중...
    docker-compose down >nul 2>&1
    echo ✅ Docker 컨테이너 종료됨
) else (
    echo ✅ 실행 중인 Docker 컨테이너가 없습니다.
)

echo.
echo ================================================
echo ✅ 모든 서버가 종료되었습니다!
echo ================================================
echo.
pause
