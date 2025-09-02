@echo off
chcp 65001 >nul
echo ================================================
echo AI 재무관리 어드바이저 - 초기 설치 스크립트
echo ================================================
echo.

echo [1/7] Python 버전 확인...
python --version
if %errorlevel% neq 0 (
    echo ❌ Python이 설치되어 있지 않습니다.
    echo Python 3.11 이상을 설치해주세요: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo.
echo [2/7] pip 업그레이드...
python -m pip install --upgrade pip

echo.
echo [3/7] 필요한 Python 패키지 설치...
echo 이 과정은 시간이 오래 걸릴 수 있습니다 (약 5-10분)...

echo.
echo [3-1/7] 기본 패키지 설치...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ⚠️  requirements.txt 설치 중 일부 오류가 발생했습니다. 개별 패키지 설치를 시도합니다.
)

echo.
echo [3-2/7] 핵심 패키지 개별 설치...
echo - streamlit 설치 중...
python -m pip install streamlit
echo - uvicorn 설치 중...
python -m pip install uvicorn[standard]
echo - fastapi 설치 중...
python -m pip install fastapi
echo - langchain 패키지들 설치 중...
python -m pip install langchain langchain-openai langchain-community
echo - langgraph 설치 중...
python -m pip install langgraph
echo - Azure OpenAI 설치 중...
python -m pip install openai azure-identity
echo - 데이터 처리 패키지들 설치 중...
python -m pip install pandas numpy yfinance
echo - 시각화 패키지들 설치 중...
python -m pip install plotly matplotlib
echo - 벡터 데이터베이스 패키지들 설치 중...
python -m pip install sentence-transformers faiss-cpu chromadb
echo - 텍스트 처리 패키지들 설치 중...
python -m pip install textblob
echo - 환경 설정 패키지들 설치 중...
python -m pip install python-dotenv pydantic-settings

echo.
echo [4/7] 환경변수 파일 생성...
if not exist .env (
    copy env_example.txt .env
    echo ✅ .env 파일이 생성되었습니다.
    echo ⚠️  .env 파일에서 Azure OpenAI API 키를 설정해주세요!
) else (
    echo ✅ .env 파일이 이미 존재합니다.
)

echo.
echo [5/7] 필요한 디렉토리 생성...
if not exist data mkdir data
if not exist data\vector_db mkdir data\vector_db
if not exist data\chroma_db mkdir data\chroma_db
if not exist data\knowledge_base mkdir data\knowledge_base
if not exist data\user_data mkdir data\user_data
if not exist logs mkdir logs
echo ✅ 디렉토리 생성 완료

echo.
echo [6/7] Docker 설치 확인...
docker --version >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Docker가 설치되어 있습니다.
) else (
    echo ⚠️  Docker가 설치되어 있지 않습니다.
    echo Docker Desktop을 설치해주세요: https://www.docker.com/products/docker-desktop/
)

echo.
echo [7/7] 핵심 패키지 설치 확인 및 추가 설치...
echo - uvicorn 확인 중...
python -c "import uvicorn; print('✅ uvicorn 설치됨')" 2>nul
if %errorlevel% neq 0 (
    echo ❌ uvicorn 설치 안됨. 설치 중...
    pip install uvicorn[standard]
    echo ✅ uvicorn 설치 완료
) else (
    echo ✅ uvicorn 이미 설치되어 있습니다.
)

echo - fastapi 확인 중...
python -c "import fastapi; print('✅ fastapi 설치됨')" 2>nul
if %errorlevel% neq 0 (
    echo ❌ fastapi 설치 안됨. 설치 중...
    pip install fastapi
    echo ✅ fastapi 설치 완료
) else (
    echo ✅ fastapi 이미 설치되어 있습니다.
)

echo - streamlit 확인 중...
python -c "import streamlit; print('✅ streamlit 설치됨')" 2>nul
if %errorlevel% neq 0 (
    echo ❌ streamlit 설치 안됨. 설치 중...
    pip install streamlit
    echo ✅ streamlit 설치 완료
) else (
    echo ✅ streamlit 이미 설치되어 있습니다.
)

echo - langchain 확인 중...
python -c "import langchain; print('✅ langchain 설치됨')" 2>nul
if %errorlevel% neq 0 (
    echo ❌ langchain 설치 안됨. 설치 중...
    pip install langchain langchain-openai langchain-community
    echo ✅ langchain 설치 완료
) else (
    echo ✅ langchain 이미 설치되어 있습니다.
)

echo - langgraph 확인 중...
python -c "import langgraph; print('✅ langgraph 설치됨')" 2>nul
if %errorlevel% neq 0 (
    echo ❌ langgraph 설치 안됨. 설치 중...
    pip install langgraph
    echo ✅ langgraph 설치 완료
) else (
    echo ✅ langgraph 이미 설치되어 있습니다.
)

echo - openai 확인 중...
python -c "import openai; print('✅ openai 설치됨')" 2>nul
if %errorlevel% equ 0 (
    echo ✅ openai 이미 설치되어 있습니다.
) else (
    echo ❌ openai 설치 안됨
)

echo - pandas 확인 중...
python -c "import pandas; print('✅ pandas 설치됨')" 2>nul
if %errorlevel% equ 0 (
    echo ✅ pandas 이미 설치되어 있습니다.
) else (
    echo ❌ pandas 설치 안됨
)

echo - textblob 확인 중...
python -c "import textblob; print('✅ textblob 설치됨')" 2>nul
if %errorlevel% equ 0 (
    echo ✅ textblob 이미 설치되어 있습니다.
) else (
    echo ❌ textblob 설치 안됨. 설치 중...
    pip install textblob
    echo ✅ textblob 설치 완료
)

echo.
echo ================================================
echo ✅ 초기 설치가 완료되었습니다!
echo ================================================
echo.
echo 다음 단계:
echo 1. .env 파일에서 Azure OpenAI API 키를 설정하세요
echo 2. 02_start_app.bat를 실행하여 서버를 시작하세요
echo 3. 또는 03_start_docker.bat를 실행하여 Docker로 실행하세요
echo.
pause
