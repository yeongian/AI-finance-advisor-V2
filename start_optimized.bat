@echo off
chcp 65001 >nul
echo 🚀 AI 재무관리 어드바이저 시작
echo ================================================

REM 환경 변수 설정
set AOAI_ENDPOINT=https://skcc-atl-dev-openai-01.openai.azure.com/
set AOAI_API_KEY=5kWBVPecvaqFeiB3PJYXnfkMHclg66duBhVXY5lWE9z187WonAnAJQQJ99BBACYeBjFXJ3w3AAABACOGqwfl
set AOAI_DEPLOY_GPT4O_MINI=gpt-4o-mini

echo ✅ 환경 변수 설정 완료

REM Python 경로 확인 (py 명령어 사용)
py --version
if %errorlevel% neq 0 (
    echo ❌ Python이 설치되지 않았습니다.
    echo 💡 Python을 설치하거나 PATH를 확인해주세요.
    echo 💡 https://www.python.org/downloads/ 에서 다운로드 가능합니다.
    pause
    exit /b 1
)

echo ✅ Python 확인 완료

echo 🚀 API 서버 시작 중...
echo 📊 서버: http://localhost:8000
echo 📚 문서: http://localhost:8000/docs
echo 💡 종료: Ctrl+C
echo.

REM API 서버 실행 (포그라운드에서 실행)
py -m uvicorn src.api.main:app --host localhost --port 8000 --reload

echo.
echo 🎉 API 서버가 종료되었습니다.
pause
