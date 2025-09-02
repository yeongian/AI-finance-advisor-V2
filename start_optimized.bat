@echo off
chcp 65001 >nul
echo ================================================
echo AI Finance Advisor - Optimized Start
echo ================================================
echo.

echo [1/4] Environment Variables Setup...
if exist .env (
    echo OK .env file exists.
) else (
    echo WARNING .env file not found. Setting environment variables directly...
    set AOAI_ENDPOINT=https://skcc-atl-dev-openai-01.openai.azure.com/
    set AOAI_API_KEY=5kWBVPecvaqFeiB3PJYXnfkMHclg66duBhVXY5lWE9z187WonAnAJQQJ99BBACYeBjFXJ3w3AAABACOGqwfl
    set AOAI_DEPLOY_GPT4O_MINI=gpt-4o-mini
    set AOAI_DEPLOY_GPT4O=gpt-4o
    set AOAI_DEPLOY_EMBED_3_LARGE=text-embedding-3-large
    set AOAI_DEPLOY_EMBED_3_SMALL=text-embedding-3-small
    set AOAI_DEPLOY_EMBED_ADA=text-embedding-ada-002
    echo OK Environment variables set.
)

echo.
echo [2/4] Server Status Check...
echo Checking port 8000 (API server)...
netstat -an | findstr :8000 >nul 2>&1
if %errorlevel% equ 0 (
    echo WARNING Port 8000 is in use. Stopping existing server...
    for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8000') do (
        taskkill /f /pid %%a >nul 2>&1
    )
    echo OK Existing API server stopped.
    timeout /t 1 /nobreak >nul
)

echo Checking port 8501 (Streamlit UI)...
netstat -an | findstr :8501 >nul 2>&1
if %errorlevel% equ 0 (
    echo WARNING Port 8501 is in use. Stopping existing server...
    for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8501') do (
        taskkill /f /pid %%a >nul 2>&1
    )
    echo OK Existing Streamlit server stopped.
    timeout /t 1 /nobreak >nul
)

echo.
echo [3/4] Starting Optimized Server...
echo Starting API server with optimized settings...
echo.

REM Start API server with optimized settings (빠른 시작)
start /b python -m uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload --log-level error --timeout-keep-alive 30 --workers 1 --limit-concurrency 100

echo API server started with optimized settings.
echo Waiting 3 seconds for API server to initialize...
timeout /t 3 /nobreak >nul

echo Starting Streamlit UI with optimized settings...
echo.
python -m streamlit run main.py --server.port 8501 --server.address 0.0.0.0 --server.maxUploadSize 200 --server.enableCORS false --server.enableXsrfProtection false

echo.
echo ================================================
echo OK Optimized application started successfully!
echo ================================================
echo.
echo Access URLs:
echo - Web UI: http://localhost:8501
echo - API Docs: http://localhost:8000/docs
echo - API Health: http://localhost:8000/health
echo.
echo TIP: Optimized for better performance and stability.
echo TIP: Access http://localhost:8501 in your browser.
echo.
pause
