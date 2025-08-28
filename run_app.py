#!/usr/bin/env python3
"""
AI 재무관리 어드바이저 실행 스크립트
"""

import os
import sys
import subprocess
import time
import requests
from pathlib import Path

def check_dependencies():
    """의존성 확인"""
    print("🔍 의존성 확인 중...")
    
    try:
        import streamlit
        import fastapi
        import langchain
        import plotly
        print("✅ 모든 의존성이 설치되어 있습니다.")
        return True
    except ImportError as e:
        print(f"❌ 의존성 누락: {e}")
        print("다음 명령어로 의존성을 설치하세요:")
        print("pip install -r requirements.txt")
        return False

def check_env_file():
    """환경변수 파일 확인"""
    print("🔍 환경변수 파일 확인 중...")
    
    env_file = Path(".env")
    if not env_file.exists():
        print("⚠️  .env 파일이 없습니다.")
        print("env_example.txt를 .env로 복사하고 API 키를 설정하세요.")
        return False
    
    # API 키 확인 (Azure OpenAI 또는 일반 OpenAI)
    with open(env_file, 'r', encoding='utf-8') as f:
        content = f.read()
        if "your_openai_api_key_here" in content and "your_actual_api_key_here" in content:
            print("⚠️  API 키가 설정되지 않았습니다.")
            print(".env 파일에서 AOAI_API_KEY 또는 OPENAI_API_KEY를 설정하세요.")
            return False
    
    print("✅ 환경변수 파일이 올바르게 설정되어 있습니다.")
    return True

def start_api_server():
    """API 서버 시작"""
    print("🚀 API 서버를 시작합니다...")
    
    try:
        # API 서버 시작
        process = subprocess.Popen([
            sys.executable, "-m", "uvicorn", 
            "src.api.main:app", 
            "--host", "0.0.0.0", 
            "--port", "8000",
            "--reload"
        ])
        
        # 서버 시작 대기
        time.sleep(5)
        
        # 헬스체크
        try:
            response = requests.get("http://localhost:8000/health", timeout=10)
            if response.status_code == 200:
                print("✅ API 서버가 성공적으로 시작되었습니다.")
                print("📖 API 문서: http://localhost:8000/docs")
                return process
            else:
                print("❌ API 서버 시작 실패")
                process.terminate()
                return None
        except requests.exceptions.RequestException:
            print("❌ API 서버에 연결할 수 없습니다.")
            process.terminate()
            return None
            
    except Exception as e:
        print(f"❌ API 서버 시작 중 오류: {e}")
        return None

def start_streamlit():
    """Streamlit UI 시작"""
    print("🚀 Streamlit UI를 시작합니다...")
    
    try:
        # Streamlit 시작
        subprocess.run([
            sys.executable, "-m", "streamlit", "run",
            "src/ui/streamlit_app.py",
            "--server.port", "8501",
            "--server.address", "0.0.0.0"
        ])
    except KeyboardInterrupt:
        print("\n👋 애플리케이션이 종료되었습니다.")
    except Exception as e:
        print(f"❌ Streamlit 시작 중 오류: {e}")

def main():
    """메인 함수"""
    print("=" * 60)
    print("💰 AI 재무관리 어드바이저")
    print("=" * 60)
    
    # 의존성 확인
    if not check_dependencies():
        sys.exit(1)
    
    # 환경변수 확인
    if not check_env_file():
        print("\n계속 진행하시겠습니까? (y/N): ", end="")
        response = input().strip().lower()
        if response != 'y':
            sys.exit(1)
    
    # API 서버 시작
    api_process = start_api_server()
    if not api_process:
        sys.exit(1)
    
    try:
        # Streamlit UI 시작
        start_streamlit()
    finally:
        # API 서버 종료
        if api_process:
            print("🛑 API 서버를 종료합니다...")
            api_process.terminate()
            api_process.wait()

if __name__ == "__main__":
    main()
