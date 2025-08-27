#!/usr/bin/env python3
"""
AI 개인 재무 관리 어드바이저 실행 스크립트
"""

import os
import sys
import subprocess
from pathlib import Path

def main():
    """메인 실행 함수"""
    
    # 프로젝트 루트 디렉토리
    project_root = Path(__file__).parent
    
    # 환경변수 파일 확인
    env_file = project_root / ".env"
    env_example = project_root / "env_example.txt"
    
    if not env_file.exists() and env_example.exists():
        print("⚠️  환경변수 파일이 설정되지 않았습니다.")
        print("다음 명령어로 환경변수 파일을 생성하세요:")
        print(f"copy {env_example} .env")
        print("그 후 .env 파일에서 OpenAI API 키를 설정하세요.")
        print()
    
    # Streamlit 앱 실행
    app_path = project_root / "src" / "ui" / "streamlit_app.py"
    
    if not app_path.exists():
        print(f"❌ 앱 파일을 찾을 수 없습니다: {app_path}")
        return
    
    print("🚀 AI 개인 재무 관리 어드바이저를 시작합니다...")
    print(f"📁 앱 경로: {app_path}")
    print("🌐 브라우저에서 http://localhost:8501 을 열어주세요.")
    print("⏹️  종료하려면 Ctrl+C를 누르세요.")
    print("-" * 50)
    
    try:
        # Streamlit 앱 실행
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", str(app_path),
            "--server.port", "8501",
            "--server.address", "localhost"
        ])
    except KeyboardInterrupt:
        print("\n👋 앱이 종료되었습니다.")
    except Exception as e:
        print(f"❌ 앱 실행 중 오류가 발생했습니다: {e}")

if __name__ == "__main__":
    main()
