"""
Azure OpenAI API 설정
강의자료 방식의 중앙집중식 환경변수 관리
"""

import os

# Azure OpenAI API 설정
AOAI_ENDPOINT = os.getenv("AOAI_ENDPOINT")
AOAI_API_KEY = os.getenv("AOAI_API_KEY")
AOAI_DEPLOY_GPT4O = os.getenv("AOAI_DEPLOY_GPT4O")
AOAI_DEPLOY_GPT4O_MINI = os.getenv("AOAI_DEPLOY_GPT4O_MINI")
AOAI_DEPLOY_EMBED_3_LARGE = os.getenv("AOAI_DEPLOY_EMBED_3_LARGE")
AOAI_DEPLOY_EMBED_3_SMALL = os.getenv("AOAI_DEPLOY_EMBED_3_SMALL")
AOAI_DEPLOY_EMBED_ADA = os.getenv("AOAI_DEPLOY_EMBED_ADA")

# API 버전
AOAI_API_VERSION = "2024-02-15-preview"

def validate_api_config():
    """API 설정 유효성 검사"""
    required_vars = [
        "AOAI_ENDPOINT",
        "AOAI_API_KEY", 
        "AOAI_DEPLOY_GPT4O_MINI",
        "AOAI_DEPLOY_EMBED_3_SMALL",
        "AOAI_DEPLOY_EMBED_ADA"
    ]
    
    missing_vars = []
    for var in required_vars:
        if not globals().get(var):
            missing_vars.append(var)
    
    if missing_vars:
        raise ValueError(f"필수 환경변수가 설정되지 않았습니다: {missing_vars}")
    
    return True

def get_endpoint_url():
    """엔드포인트 URL 정규화"""
    if AOAI_ENDPOINT and not AOAI_ENDPOINT.endswith('/'):
        return AOAI_ENDPOINT + '/'
    return AOAI_ENDPOINT
