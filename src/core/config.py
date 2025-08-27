"""
설정 관리 모듈
환경변수와 애플리케이션 설정을 관리합니다.
"""

import os
from typing import Optional
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

class Config:
    """애플리케이션 설정 클래스"""
    
    # Azure OpenAI 설정 (우선순위)
    AOAI_ENDPOINT: str = os.getenv("AOAI_ENDPOINT", "")
    AOAI_API_KEY: str = os.getenv("AOAI_API_KEY", "")
    AOAI_DEPLOY_GPT4O_MINI: str = os.getenv("AOAI_DEPLOY_GPT4O_MINI", "gpt-4o-mini")
    AOAI_DEPLOY_GPT4O: str = os.getenv("AOAI_DEPLOY_GPT4O", "gpt-4o")
    AOAI_DEPLOY_EMBED_3_LARGE: str = os.getenv("AOAI_DEPLOY_EMBED_3_LARGE", "text-embedding-3-large")
    AOAI_DEPLOY_EMBED_3_SMALL: str = os.getenv("AOAI_DEPLOY_EMBED_3_SMALL", "text-embedding-3-small")
    AOAI_DEPLOY_EMBED_ADA: str = os.getenv("AOAI_DEPLOY_EMBED_ADA", "text-embedding-ada-002")
    AOAI_API_VERSION: str = "2024-02-15-preview"
    
    # OpenAI 설정 (백업)
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_API_BASE: str = os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1")
    
    # 데이터베이스 설정
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./finance_advisor.db")
    
    # 벡터 데이터베이스 설정
    VECTOR_DB_PATH: str = os.getenv("VECTOR_DB_PATH", "./vector_db")
    
    # 로깅 설정
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE: str = os.getenv("LOG_FILE", "./logs/finance_advisor.log")
    
    # 서버 설정
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    DEBUG: bool = os.getenv("DEBUG", "True").lower() == "true"
    
    # 금융 API 설정 (선택사항)
    ALPHA_VANTAGE_API_KEY: Optional[str] = os.getenv("ALPHA_VANTAGE_API_KEY")
    FRED_API_KEY: Optional[str] = os.getenv("FRED_API_KEY")
    
    # 보안 설정
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-this")
    
    # AI 모델 설정 (Azure OpenAI 우선)
    DEFAULT_MODEL: str = AOAI_DEPLOY_GPT4O_MINI if AOAI_ENDPOINT and AOAI_API_KEY else "gpt-4o-mini"
    EMBEDDING_MODEL: str = AOAI_DEPLOY_EMBED_3_SMALL if AOAI_ENDPOINT and AOAI_API_KEY else "text-embedding-3-small"
    
    # RAG 설정
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 200
    TOP_K_RESULTS: int = 5
    
    @classmethod
    def validate(cls) -> bool:
        """필수 설정값 검증"""
        if not cls.AOAI_ENDPOINT or not cls.AOAI_API_KEY:
            if not cls.OPENAI_API_KEY:
                print("⚠️  경고: Azure OpenAI 또는 OpenAI API 키가 설정되지 않았습니다.")
                print("   env_example.txt를 .env로 복사하고 API 키를 설정하세요.")
                return False
        return True
    
    @classmethod
    def get_openai_config(cls) -> dict:
        """OpenAI 설정 반환 (Azure OpenAI 우선)"""
        # Azure OpenAI 사용 가능한 경우
        if cls.AOAI_ENDPOINT and cls.AOAI_API_KEY:
            return {
                "api_key": cls.AOAI_API_KEY,
                "base_url": cls.AOAI_ENDPOINT,
                "api_version": cls.AOAI_API_VERSION
            }
        
        # 일반 OpenAI 사용
        return {
            "api_key": cls.OPENAI_API_KEY,
            "base_url": cls.OPENAI_API_BASE
        }
    
    @classmethod
    def is_azure_openai(cls) -> bool:
        """Azure OpenAI 사용 여부 확인"""
        return bool(cls.AOAI_ENDPOINT and cls.AOAI_API_KEY)

# 전역 설정 인스턴스
config = Config()
