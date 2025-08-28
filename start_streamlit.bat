@echo off
chcp 65001 >nul
echo 🌐 AI 재무관리 어드바이저 Streamlit 앱 시작
echo ================================================

REM Python 경로 확인
py --version
if %errorlevel% neq 0 (
    echo ❌ Python이 설치되지 않았습니다.
    pause
    exit /b 1
)

echo ✅ Python 확인 완료

echo 🌐 Streamlit 앱 시작 중...
echo 📊 웹 인터페이스: http://localhost:8501
echo 💡 종료: Ctrl+C
echo.

REM Streamlit 앱 실행 (main.py 사용)
py -m streamlit run main.py --server.port 8501

echo.
echo 🎉 Streamlit 앱이 종료되었습니다.
pause
