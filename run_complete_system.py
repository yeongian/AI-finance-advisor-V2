#!/usr/bin/env python3
"""
AI 재무관리 어드바이저 - 완전한 시스템 실행 스크립트
RAG + Multi Agent + Streamlit UI
"""

import subprocess
import sys
import time
import threading
import os
from pathlib import Path

def run_api_server():
    """API 서버 실행 (RAG + Multi Agent)"""
    print("🚀 API 서버를 시작합니다... (RAG + Multi Agent)")
    try:
        subprocess.run([
            sys.executable, "-m", "uvicorn", 
            "src.api.main:app",
            "--host", "localhost",
            "--port", "8000",
            "--reload",
            "--reload-dir", "src"
        ], check=True)
    except KeyboardInterrupt:
        print("API 서버가 종료되었습니다.")
    except Exception as e:
        print(f"API 서버 실행 중 오류: {e}")

def run_streamlit_server():
    """Streamlit 웹 서버 실행"""
    print("🌐 Streamlit 웹 서버를 시작합니다...")
    try:
        subprocess.run([
            sys.executable, "-m", "streamlit", "run",
            "simple_streamlit_app.py",
            "--server.port", "8501",
            "--server.address", "localhost"
        ], check=True)
    except KeyboardInterrupt:
        print("Streamlit 서버가 종료되었습니다.")
    except Exception as e:
        print(f"Streamlit 서버 실행 중 오류: {e}")

def main():
    """메인 실행 함수"""
    print("=" * 70)
    print("💰 AI 재무관리 어드바이저 - 완전한 시스템")
    print("=" * 70)
    print("📍 API 서버: http://localhost:8000")
    print("📖 API 문서: http://localhost:8000/docs")
    print("🌐 웹 인터페이스: http://localhost:8501")
    print("🔍 RAG 검색: http://localhost:8000/rag/search")
    print("🤖 에이전트 정보: http://localhost:8000/agents/info")
    print("=" * 70)
    
    # 현재 디렉토리 확인
    current_dir = Path.cwd()
    print(f"현재 디렉토리: {current_dir}")
    
    # 프로젝트 루트로 이동
    if not (current_dir / "src").exists():
        print("❌ src 디렉토리를 찾을 수 없습니다.")
        print("프로젝트 루트 디렉토리에서 실행해주세요.")
        return
    
    # 환경변수 확인
    required_env_vars = ["AOAI_API_KEY", "AOAI_ENDPOINT", "AOAI_DEPLOY_GPT4O_MINI"]
    missing_vars = [var for var in required_env_vars if not os.getenv(var)]
    
    if missing_vars:
        print("❌ 다음 환경변수가 설정되지 않았습니다:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\n.env 파일을 확인하거나 환경변수를 설정해주세요.")
        return
    
    print("✅ 환경변수 확인 완료")
    
    # 두 서버를 별도 스레드에서 실행
    api_thread = threading.Thread(target=run_api_server, daemon=True)
    streamlit_thread = threading.Thread(target=run_streamlit_server, daemon=True)
    
    try:
        # API 서버 시작
        api_thread.start()
        print("✅ API 서버 시작됨")
        
        # 잠시 대기 (RAG + Multi Agent 초기화 시간)
        print("⏳ RAG 및 Multi Agent 시스템 초기화 중...")
        time.sleep(10)
        
        # Streamlit 서버 시작
        streamlit_thread.start()
        print("✅ Streamlit 서버 시작됨")
        
        print("\n🎉 모든 서버가 시작되었습니다!")
        print("웹 브라우저에서 http://localhost:8501 로 접속하세요.")
        print("종료하려면 Ctrl+C를 누르세요.")
        
        # 메인 스레드 대기
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n🛑 서버를 종료합니다...")
        print("잠시만 기다려주세요...")
        time.sleep(2)
        print("✅ 모든 서버가 종료되었습니다.")

if __name__ == "__main__":
    main()
