@echo off
chcp 65001 >nul
echo ============================================================
echo Environment Variables Setup and Server Execution
echo ============================================================

REM Set environment variables
set AOAI_ENDPOINT=https://skcc-atl-dev-openai-01.openai.azure.com/
set AOAI_API_KEY=5kWBVPecvaqFeiB3PJYXnfkMHclg66duBhVXY5lWE9z187WonAnAJQQJ99BBACOGqwfl
set AOAI_DEPLOY_GPT4O_MINI=gpt-4o-mini

echo Environment variables set:
echo AOAI_ENDPOINT: %AOAI_ENDPOINT%
echo AOAI_API_KEY: %AOAI_API_KEY%
echo AOAI_DEPLOY_GPT4O_MINI: %AOAI_DEPLOY_GPT4O_MINI%
echo ============================================================

REM Execute server
py run_complete_system.py

pause
