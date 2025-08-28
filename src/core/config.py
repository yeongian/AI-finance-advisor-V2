"""
설정 관리 모듈
환경변수와 애플리케이션 설정을 관리합니다.
"""

import os
from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

class Settings(BaseSettings):
    """애플리케이션 설정 클래스"""
    
    # Azure OpenAI 설정
    aoai_endpoint: Optional[str] = os.getenv("AOAI_ENDPOINT")
    aoai_api_key: Optional[str] = os.getenv("AOAI_API_KEY")
    aoai_deploy_gpt4o_mini: str = os.getenv("AOAI_DEPLOY_GPT4O_MINI", "gpt-4o-mini")
    aoai_deploy_gpt4o: str = os.getenv("AOAI_DEPLOY_GPT4O", "gpt-4o")
    aoai_deploy_embed_3_large: str = os.getenv("AOAI_DEPLOY_EMBED_3_LARGE", "text-embedding-3-large")
    aoai_deploy_embed_3_small: str = os.getenv("AOAI_DEPLOY_EMBED_3_SMALL", "text-embedding-3-small")
    aoai_deploy_embed_ada: str = os.getenv("AOAI_DEPLOY_EMBED_ADA", "text-embedding-ada-002")
    
    # OpenAI 설정 (Azure OpenAI 사용 시 백업)
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    embedding_model: str = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
    
    # Azure OpenAI 사용 여부 확인
    @property
    def use_azure_openai(self) -> bool:
        """Azure OpenAI 사용 여부를 반환합니다."""
        return bool(self.aoai_endpoint and self.aoai_api_key)
    
    # 금융 데이터 API
    alpha_vantage_api_key: Optional[str] = os.getenv("ALPHA_VANTAGE_API_KEY")
    yahoo_finance_api_key: Optional[str] = os.getenv("YAHOO_FINANCE_API_KEY")
    
    # 데이터베이스 설정
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./data/finance_advisor.db")
    
    # 벡터 데이터베이스 설정
    vector_db_path: str = os.getenv("VECTOR_DB_PATH", "./data/vector_db")
    chroma_db_path: str = os.getenv("CHROMA_DB_PATH", "./data/chroma_db")
    
    # 로깅 설정
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    log_file: str = os.getenv("LOG_FILE", "./logs/app.log")
    
    # 서버 설정
    host: str = os.getenv("HOST", "0.0.0.0")
    port: int = int(os.getenv("PORT", "8000"))
    debug: bool = os.getenv("DEBUG", "True").lower() == "true"
    
    # 보안 설정
    secret_key: str = os.getenv("SECRET_KEY", "your-secret-key-change-this")
    access_token_expire_minutes: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    
    # RAG 설정
    rag_chunk_size: int = int(os.getenv("RAG_CHUNK_SIZE", "1000"))
    rag_chunk_overlap: int = int(os.getenv("RAG_CHUNK_OVERLAP", "200"))
    rag_top_k: int = int(os.getenv("RAG_TOP_K", "5"))
    
    # 에이전트 설정
    max_tokens: int = int(os.getenv("MAX_TOKENS", "4000"))
    temperature: float = float(os.getenv("TEMPERATURE", "0.7"))
    max_iterations: int = int(os.getenv("MAX_ITERATIONS", "10"))
    
    class Config:
        env_file = ".env"
        case_sensitive = False

# 전역 설정 인스턴스
settings = Settings()

def get_project_root() -> Path:
    """프로젝트 루트 디렉토리 반환"""
    return Path(__file__).parent.parent.parent

def ensure_directories():
    """필요한 디렉토리들을 생성합니다."""
    directories = [
        "data",
        "data/knowledge_base",
        "data/user_data",
        "data/vector_db",
        "data/chroma_db",
        "logs"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)

# 애플리케이션 시작 시 디렉토리 생성
ensure_directories()
