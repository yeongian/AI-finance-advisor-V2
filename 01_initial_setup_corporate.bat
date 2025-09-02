@echo off
chcp 65001 >nul
echo ================================================
echo AI 재무관리 어드바이저 - 사내망 초기 설치 스크립트
echo ================================================
echo.

echo [1/6] Python 버전 확인...
python --version
if %errorlevel% neq 0 (
    echo ❌ Python이 설치되어 있지 않습니다.
    echo Python 3.11 이상을 설치해주세요: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo.
echo [2/6] pip 업그레이드...
python -m pip install --upgrade pip

echo.
echo [3/6] 필요한 Python 패키지 설치 (사내망용)...
echo 이 과정은 시간이 오래 걸릴 수 있습니다 (약 5-10분)...

echo.
echo [3-1/6] 기본 패키지 설치 (plotly 제외)...
echo 사내망에서는 plotly 설치가 제한될 수 있습니다.
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ⚠️  requirements.txt 설치 중 일부 오류가 발생했습니다. 개별 패키지 설치를 시도합니다.
)

echo.
echo [3-2/6] 핵심 패키지 개별 설치...
echo - 웹 프레임워크 설치 중...
python -m pip install streamlit uvicorn[standard] fastapi

echo - AI/ML 패키지 설치 중...
python -m pip install langchain langchain-openai langchain-community langgraph

echo - Azure OpenAI 설치 중...
python -m pip install openai azure-identity

echo - 데이터 처리 패키지 설치 중...
python -m pip install pandas numpy yfinance

echo - 시각화 패키지 설치 중 (plotly 제외)...
python -m pip install matplotlib

echo - 벡터 데이터베이스 패키지 설치 중...
python -m pip install sentence-transformers faiss-cpu chromadb

echo - 텍스트 처리 패키지 설치 중...
python -m pip install textblob

echo - 환경 설정 패키지 설치 중...
python -m pip install python-dotenv pydantic-settings

echo.
echo [3-3/6] plotly 선택적 설치 시도...
echo plotly 설치를 시도합니다 (사내망 정책에 따라 실패할 수 있음)...
python -m pip install plotly
if %errorlevel% equ 0 (
    echo ✅ plotly 설치 성공!
    echo plotly 상세 정보:
    pip show plotly
) else (
    echo ⚠️  plotly 설치 실패 (사내망 정책으로 인한 제한일 수 있음)
    echo 앱은 plotly 없이도 정상 작동합니다.
)

echo.
echo [4/6] 환경변수 파일 생성...
if not exist .env (
    copy env_example.txt .env
    echo ✅ .env 파일이 생성되었습니다.
    echo ⚠️  .env 파일에서 Azure OpenAI API 키를 설정해주세요!
) else (
    echo ✅ .env 파일이 이미 존재합니다.
)

echo.
echo [5/6] 필요한 디렉토리 생성...
if not exist data mkdir data
if not exist data\vector_db mkdir data\vector_db
if not exist data\chroma_db mkdir data\chroma_db
if not exist data\knowledge_base mkdir data\knowledge_base
if not exist data\user_data mkdir data\user_data
if not exist logs mkdir logs
echo ✅ 디렉토리 생성 완료

echo.
echo [6/6] 핵심 패키지 설치 확인...
echo - 웹 프레임워크 확인 중...
python -c "import streamlit, uvicorn, fastapi; print('✅ 웹 프레임워크 설치됨')" 2>nul
if %errorlevel% neq 0 (
    echo ❌ 웹 프레임워크 설치 안됨. 재설치 중...
    pip install streamlit uvicorn[standard] fastapi
)

echo - AI/ML 패키지 확인 중...
python -c "import langchain, langgraph, openai; print('✅ AI/ML 패키지 설치됨')" 2>nul
if %errorlevel% neq 0 (
    echo ❌ AI/ML 패키지 설치 안됨. 재설치 중...
    pip install langchain langchain-openai langchain-community langgraph openai
)

echo - 데이터 처리 패키지 확인 중...
python -c "import pandas, numpy, yfinance; print('✅ 데이터 처리 패키지 설치됨')" 2>nul
if %errorlevel% neq 0 (
    echo ❌ 데이터 처리 패키지 설치 안됨. 재설치 중...
    pip install pandas numpy yfinance
)

echo - plotly 확인 중...
python -c "import plotly; print('✅ plotly 설치됨')" 2>nul
if %errorlevel% equ 0 (
    echo ✅ plotly 설치됨 - 차트 기능 사용 가능
) else (
    echo ⚠️  plotly 설치 안됨 - 차트 기능 제한됨
)

echo.
echo ================================================
echo ✅ 사내망 초기 설치가 완료되었습니다!
echo ================================================
echo.
echo 다음 단계:
echo 1. .env 파일에서 Azure OpenAI API 키를 설정하세요
echo 2. 02_start_app.bat를 실행하여 서버를 시작하세요
echo 3. plotly가 설치되지 않은 경우 차트 기능이 제한됩니다
echo.
pause
