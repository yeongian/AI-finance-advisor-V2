"""
FastAPI 메인 애플리케이션
AI 재무관리 어드바이저의 REST API 서버 (RAG + Multi Agent 통합)
"""

import logging
import time
from typing import Dict, Any, List, Optional
from datetime import datetime

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
import uvicorn

from ..core.config import settings
from ..rag.knowledge_base import KnowledgeBase
from ..agents.multi_agent_system import MultiAgentSystem

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 성능 측정을 위한 전역 변수
startup_times = {}

def log_performance(step_name: str, start_time: float):
    """성능 측정 로깅"""
    elapsed = time.time() - start_time
    startup_times[step_name] = elapsed
    logger.info(f"⏱️ {step_name} 완료: {elapsed:.2f}초")

# FastAPI 앱 생성
app = FastAPI(
    title="AI 재무관리 어드바이저 API",
    description="개인 재무 관리를 위한 AI 어드바이저 API (RAG + Multi Agent)",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 프로덕션에서는 특정 도메인으로 제한
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 전역 변수
knowledge_base = None
multi_agent_system = None

# Pydantic 모델들
class UserData(BaseModel):
    """사용자 데이터 모델"""
    age: int = Field(..., ge=18, le=100, description="나이")
    income: float = Field(..., ge=0, description="연소득")
    expenses: float = Field(..., ge=0, description="연지출")
    savings: float = Field(..., ge=0, description="저축액")
    risk_tolerance: str = Field(default="moderate", description="위험 성향")
    monthly_expenses: Optional[Dict[str, float]] = Field(default=None, description="월별 지출")
    current_investments: Optional[Dict[str, float]] = Field(default=None, description="현재 투자")
    
    class Config:
        schema_extra = {
            "example": {
                "age": 30,
                "income": 50000000,
                "expenses": 30000000,
                "savings": 10000000,
                "risk_tolerance": "moderate",
                "monthly_expenses": {
                    "housing": 800000,
                    "food": 500000,
                    "transportation": 300000,
                    "utilities": 200000,
                    "entertainment": 200000
                },
                "current_investments": {
                    "stocks": 5000000,
                    "bonds": 2000000,
                    "cash": 3000000
                }
            }
        }

class QueryRequest(BaseModel):
    """쿼리 요청 모델"""
    query: str = Field(..., min_length=1, description="사용자 질문")
    user_data: Optional[UserData] = Field(default=None, description="사용자 데이터")

class AnalysisRequest(BaseModel):
    """분석 요청 모델"""
    analysis_type: str = Field(..., description="분석 유형")
    user_data: UserData = Field(..., description="사용자 데이터")

class ComprehensiveAnalysisRequest(BaseModel):
    """종합 분석 요청 모델"""
    user_data: UserData = Field(..., description="사용자 데이터")

# 의존성 함수들
async def get_knowledge_base():
    """지식베이스 의존성 (지연 로딩)"""
    global knowledge_base
    if knowledge_base is None:
        try:
            from ..rag.knowledge_base import KnowledgeBase
            logger.info("📚 지식베이스 지연 로딩 시작...")
            knowledge_base = KnowledgeBase()
            success = knowledge_base.initialize()
            if not success:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="지식베이스 초기화 실패"
                )
            logger.info("📚 지식베이스 지연 로딩 완료")
        except ImportError as e:
            logger.error(f"지식베이스 모듈 임포트 실패: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="지식베이스 모듈을 찾을 수 없습니다"
            )
    return knowledge_base

async def get_multi_agent_system():
    """멀티 에이전트 시스템 의존성 (지연 로딩)"""
    global multi_agent_system
    if multi_agent_system is None:
        try:
            from ..agents.multi_agent_system import MultiAgentSystem
            logger.info("🤖 멀티 에이전트 시스템 지연 로딩 시작...")
            multi_agent_system = MultiAgentSystem()
            kb = await get_knowledge_base()
            success = multi_agent_system.initialize(kb)
            if not success:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="멀티 에이전트 시스템 초기화 실패"
                )
            logger.info("🤖 멀티 에이전트 시스템 지연 로딩 완료")
        except ImportError as e:
            logger.error(f"멀티 에이전트 시스템 모듈 임포트 실패: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="멀티 에이전트 시스템 모듈을 찾을 수 없습니다"
            )
    return multi_agent_system

# 라우트 정의
@app.get("/")
async def root():
    """루트 엔드포인트"""
    return {
        "message": "AI 재무관리 어드바이저 API (RAG + Multi Agent)",
        "version": "2.0.0",
        "status": "running",
        "features": ["RAG", "Multi Agent", "Streamlit UI"],
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health")
async def health_check():
    """헬스 체크"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "knowledge_base": knowledge_base is not None,
            "multi_agent_system": multi_agent_system is not None
        }
    }

@app.post("/query", response_model=Dict[str, Any])
async def process_query(
    request: QueryRequest,
    agent_system: MultiAgentSystem = Depends(get_multi_agent_system)
):
    """
    사용자 쿼리 처리 (RAG + Multi Agent)
    
    Args:
        request: 쿼리 요청
        agent_system: 멀티 에이전트 시스템
        
    Returns:
        AI 응답
    """
    try:
        user_data = request.user_data.dict() if request.user_data else {}
        response = agent_system.process_query(request.query, user_data)
        
        return {
            "query": request.query,
            "response": response,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"쿼리 처리 실패: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"쿼리 처리 중 오류가 발생했습니다: {str(e)}"
        )

@app.post("/analyze/{analysis_type}", response_model=Dict[str, Any])
async def analyze_financial_data(
    analysis_type: str,
    request: AnalysisRequest,
    agent_system: MultiAgentSystem = Depends(get_multi_agent_system)
):
    """
    특정 재무 분석 수행
    
    Args:
        analysis_type: 분석 유형 (budget, investment, tax, retirement)
        request: 분석 요청
        agent_system: 멀티 에이전트 시스템
        
    Returns:
        분석 결과
    """
    try:
        if analysis_type not in ["budget", "investment", "tax", "retirement"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"지원하지 않는 분석 유형: {analysis_type}"
            )
        
        result = agent_system.get_specialized_analysis(
            analysis_type, 
            request.user_data.dict()
        )
        
        return {
            "analysis_type": analysis_type,
            "result": result,
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"분석 실패: {analysis_type}, {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"분석 중 오류가 발생했습니다: {str(e)}"
        )

@app.post("/comprehensive-analysis", response_model=Dict[str, Any])
async def comprehensive_analysis(
    request: ComprehensiveAnalysisRequest,
    agent_system: MultiAgentSystem = Depends(get_multi_agent_system)
):
    """
    종합 재무 분석 수행
    
    Args:
        request: 종합 분석 요청
        agent_system: 멀티 에이전트 시스템
        
    Returns:
        종합 분석 결과
    """
    try:
        result = agent_system.get_comprehensive_analysis(request.user_data.dict())
        
        return {
            "analysis_type": "comprehensive",
            "result": result,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"종합 분석 실패: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"종합 분석 중 오류가 발생했습니다: {str(e)}"
        )

@app.get("/agents/info", response_model=Dict[str, Any])
async def get_agent_info(
    agent_system: MultiAgentSystem = Depends(get_multi_agent_system)
):
    """에이전트 시스템 정보 조회"""
    try:
        return agent_system.get_agent_info()
    except Exception as e:
        logger.error(f"에이전트 정보 조회 실패: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"에이전트 정보 조회 중 오류가 발생했습니다: {str(e)}"
        )

@app.get("/knowledge-base/stats", response_model=Dict[str, Any])
async def get_knowledge_base_stats(
    kb: KnowledgeBase = Depends(get_knowledge_base)
):
    """지식베이스 통계 조회"""
    try:
        return kb.get_statistics()
    except Exception as e:
        logger.error(f"지식베이스 통계 조회 실패: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"지식베이스 통계 조회 중 오류가 발생했습니다: {str(e)}"
        )

@app.post("/agents/clear-memory")
async def clear_agent_memory(
    agent_system: MultiAgentSystem = Depends(get_multi_agent_system)
):
    """에이전트 메모리 초기화"""
    try:
        agent_system.clear_all_memories()
        return {"message": "모든 에이전트의 메모리가 초기화되었습니다."}
    except Exception as e:
        logger.error(f"메모리 초기화 실패: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"메모리 초기화 중 오류가 발생했습니다: {str(e)}"
        )

@app.get("/sample-queries", response_model=List[str])
async def get_sample_queries(
    kb: KnowledgeBase = Depends(get_knowledge_base)
):
    """샘플 쿼리 목록 조회"""
    try:
        return kb.get_sample_queries()
    except Exception as e:
        logger.error(f"샘플 쿼리 조회 실패: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"샘플 쿼리 조회 중 오류가 발생했습니다: {str(e)}"
        )

@app.get("/rag/search")
async def search_knowledge_base(
    query: str,
    k: int = 5,
    kb: KnowledgeBase = Depends(get_knowledge_base)
):
    """지식베이스 검색"""
    try:
        docs = kb.search(query, k=k)
        return {
            "query": query,
            "results": [
                {
                    "content": doc.page_content,
                    "metadata": doc.metadata
                }
                for doc in docs
            ],
            "count": len(docs)
        }
    except Exception as e:
        logger.error(f"지식베이스 검색 실패: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"검색 중 오류가 발생했습니다: {str(e)}"
        )

# 예외 처리
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """전역 예외 처리"""
    logger.error(f"전역 예외 발생: {exc}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "서버 내부 오류가 발생했습니다.",
            "timestamp": datetime.now().isoformat()
        }
    )

# 시작 이벤트 (최적화)
@app.on_event("startup")
async def startup_event():
    """애플리케이션 시작 시 실행 (최적화된 버전)"""
    total_start_time = time.time()
    logger.info("🚀 AI 재무관리 어드바이저 API 서버 시작 중...")
    
    # 기본 서버만 시작하고, 무거운 컴포넌트는 지연 로딩으로 처리
    logger.info("⚡ 빠른 시작을 위해 지연 로딩 모드로 실행됩니다.")
    logger.info("📚 지식베이스와 멀티 에이전트는 첫 요청 시 로드됩니다.")
    
    # 전체 시작 시간 로깅
    total_elapsed = time.time() - total_start_time
    logger.info(f"✅ 서버 시작 완료! 총 소요시간: {total_elapsed:.2f}초")
    logger.info("🎯 이제 API 요청을 받을 준비가 되었습니다!")

# 종료 이벤트
@app.on_event("shutdown")
async def shutdown_event():
    """애플리케이션 종료 시 실행"""
    logger.info("AI 재무관리 어드바이저 API 서버가 종료되었습니다.")

# 직접 실행 시
if __name__ == "__main__":
    uvicorn.run(
        "src.api.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level="info"
    )
