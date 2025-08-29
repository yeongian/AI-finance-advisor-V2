@echo off
echo ================================================
echo AI 재무관리 어드바이저 - Docker 실행
echo ================================================
echo.

echo [1/5] Docker 설치 확인...
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker가 설치되어 있지 않습니다.
    echo Docker Desktop을 설치해주세요: https://www.docker.com/products/docker-desktop/
    pause
    exit /b 1
)
echo ✅ Docker 확인 완료

echo.
echo [2/5] Docker 서비스 상태 확인...
docker info >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker 서비스가 실행되지 않았습니다.
    echo Docker Desktop을 시작해주세요.
    pause
    exit /b 1
)
echo ✅ Docker 서비스 확인 완료

echo.
echo [3/5] 환경변수 파일 확인...
if not exist .env (
    echo ❌ .env 파일이 없습니다.
    echo 01_initial_setup.bat을 먼저 실행해주세요.
    pause
    exit /b 1
)
echo ✅ .env 파일 확인 완료

echo.
echo [4/5] Docker 이미지 빌드...
echo 이 과정은 처음 실행 시 시간이 오래 걸릴 수 있습니다 (약 10-15분)...
docker-compose build
if %errorlevel% neq 0 (
    echo ❌ Docker 이미지 빌드 중 오류가 발생했습니다.
    pause
    exit /b 1
)
echo ✅ Docker 이미지 빌드 완료

echo.
echo [5/5] Docker 컨테이너 시작...
docker-compose up -d
if %errorlevel% neq 0 (
    echo ❌ Docker 컨테이너 시작 중 오류가 발생했습니다.
    pause
    exit /b 1
)

echo.
echo ================================================
echo ✅ Docker 컨테이너가 시작되었습니다!
echo ================================================
echo.
echo 접속 주소:
echo - 웹 UI: http://localhost:8501
echo - API 문서: http://localhost:8000/docs
echo - API 상태: http://localhost:8000/health
echo.
echo Docker 컨테이너 관리:
echo - 컨테이너 상태 확인: docker-compose ps
echo - 로그 확인: docker-compose logs -f
echo - 컨테이너 중지: docker-compose down
echo.
pause
