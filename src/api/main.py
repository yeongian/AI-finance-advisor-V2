"""
FastAPI 메인 애플리케이션
AI 재무관리 어드바이저의 REST API 서버 (RAG + Multi Agent 통합)
"""

import logging
import time
import asyncio
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
from ..core.financial_data import financial_data
from ..core.portfolio_simulator import portfolio_simulator
from ..core.advanced_ai import advanced_ai
# 중복된 라우터 import 제거 - 메인 API만 사용

# 로깅 설정 (UTF-8 인코딩으로 설정)
import sys
import os

# 로그 디렉토리 생성
os.makedirs('logs', exist_ok=True)

# 콘솔 출력용 핸들러 (이모지 제거 및 인코딩 처리)
class ConsoleHandler(logging.StreamHandler):
    def emit(self, record):
        try:
            # 이모지 제거
            msg = self.format(record)
            msg = msg.replace('🚀', '[START]').replace('⚡', '[FAST]').replace('📚', '[KB]')
            msg = msg.replace('🌐', '[API]').replace('✅', '[OK]').replace('🎯', '[TARGET]')
            msg = msg.replace('🔄', '[LOAD]').replace('🤖', '[AI]').replace('🎉', '[SUCCESS]')
            msg = msg.replace('💡', '[TIP]').replace('⚠️', '[WARN]').replace('❌', '[ERROR]')
            msg = msg.replace('💰', '[MONEY]').replace('📈', '[INVEST]').replace('🧾', '[TAX]')
            msg = msg.replace('🏠', '[REALESTATE]').replace('💳', '[CARD]').replace('📊', '[ANALYSIS]')
            msg = msg.replace('💬', '[CHAT]').replace('📋', '[INFO]').replace('🔧', '[FIX]')
            msg = msg.replace('🔍', '[CHECK]').replace('📝', '[SAMPLE]').replace('💭', '[QUESTION]')
            msg = msg.replace('🗑️', '[CLEAR]').replace('🤖', '[AI]').replace('📚', '[KB]')
            
            # UTF-8 인코딩으로 안전하게 출력
            try:
                stream = self.stream
                stream.write(msg + self.terminator)
                self.flush()
            except UnicodeEncodeError:
                # 인코딩 오류 시 ASCII로 변환
                safe_msg = msg.encode('ascii', errors='ignore').decode('ascii')
                stream.write(safe_msg + self.terminator)
                self.flush()
        except Exception:
            self.handleError(record)

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        ConsoleHandler(sys.stdout),
        logging.FileHandler('logs/app.log', encoding='utf-8')
    ]
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

# favicon.ico 404 에러 해결
from fastapi.responses import Response

@app.get("/favicon.ico")
async def favicon():
    """favicon.ico 요청 처리"""
    return Response(status_code=204)  # No Content 응답

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 프로덕션에서는 특정 도메인으로 제한
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 중복된 라우터 제거 - 메인 API만 사용

# 전역 변수
knowledge_base = None
multi_agent_system = None
routers_loaded = False
is_initializing = False  # 초기화 중복 방지

# 지연 라우터 로딩 함수
def load_routers():
    """라우터를 지연 로딩으로 로드"""
    global routers_loaded
    if not routers_loaded:
        try:
            logger.info("[LOAD] 라우터 지연 로딩 시작...")
            app.include_router(enhanced_router)
            app.include_router(advanced_tool_router)
            app.include_router(langgraph_router)
            routers_loaded = True
            logger.info("[OK] 라우터 지연 로딩 완료")
        except Exception as e:
            logger.error(f"[ERROR] 라우터 로딩 실패: {e}")

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
    global knowledge_base, is_initializing
    
    # 이미 초기화된 경우 바로 반환
    if knowledge_base is not None and knowledge_base.is_initialized:
        return knowledge_base
    
    # 초기화 중인 경우 대기
    if is_initializing:
        logger.info("[KB] 지식베이스 초기화 중... 대기")
        while is_initializing:
            await asyncio.sleep(0.1)
        return knowledge_base
    
    # 초기화 시작
    is_initializing = True
    try:
        from ..rag.knowledge_base import KnowledgeBase
        logger.info("[KB] 지식베이스 지연 로딩 시작...")
        knowledge_base = KnowledgeBase()
        success = knowledge_base.initialize()
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="지식베이스 초기화 실패"
            )
        logger.info("[KB] 지식베이스 지연 로딩 완료")
    except ImportError as e:
        is_initializing = False
        logger.error(f"지식베이스 모듈 임포트 실패: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="지식베이스 모듈을 찾을 수 없습니다"
        )
    except Exception as e:
        is_initializing = False
        logger.error(f"지식베이스 초기화 실패: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"지식베이스 초기화 실패: {str(e)}"
        )
    finally:
        is_initializing = False
    
    return knowledge_base

async def get_multi_agent_system():
    """멀티 에이전트 시스템 의존성 (지연 로딩)"""
    global multi_agent_system
    if multi_agent_system is None:
        try:
            from ..agents.multi_agent_system import MultiAgentSystem
            logger.info("[AI] 멀티 에이전트 시스템 지연 로딩 시작...")
            multi_agent_system = MultiAgentSystem()
            kb = await get_knowledge_base()
            success = multi_agent_system.initialize(kb)
            if not success:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="멀티 에이전트 시스템 초기화 실패"
                )
            logger.info("[AI] 멀티 에이전트 시스템 지연 로딩 완료")
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
    # 첫 요청 시 라우터 로딩
    load_routers()
    
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
@app.get("/query")
async def process_query(
    request: QueryRequest = None,
    q: str = None,
    agent_system: MultiAgentSystem = Depends(get_multi_agent_system)
):
    # GET 요청 처리
    if request is None:
        if q:
            request = QueryRequest(query=q, user_data=None)
        else:
            # q 파라미터도 없는 경우 기본 응답
            return {
                "query": "",
                "answer": "AI 재무관리 어드바이저에 오신 것을 환영합니다! 질문을 입력해주세요.",
                "agent_type": "welcome",
                "context_used": False,
                "timestamp": datetime.now().isoformat()
            }
    
    """
    사용자 쿼리 처리 (RAG + Multi Agent)
    
    Args:
        request: 쿼리 요청 (POST) 또는 q: 쿼리 문자열 (GET)
        agent_system: 멀티 에이전트 시스템
        
    Returns:
        AI 응답
    """
    try:
        # 지식베이스 가져오기 (이미 초기화된 경우 빠르게 반환)
        kb = await get_knowledge_base()
        
        # 멀티 에이전트 시스템에 지식베이스 전달
        if agent_system.knowledge_base is None:
            logger.info("멀티 에이전트 시스템에 지식베이스 연결 중...")
            agent_system.knowledge_base = kb
        
        user_data = request.user_data.dict() if request.user_data else {}
        response = agent_system.process_query(request.query, user_data)
        
        return {
            "query": request.query,
            "answer": response,
            "agent_type": "comprehensive",
            "context_used": True,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"쿼리 처리 실패: {e}")
        
        # 지식베이스 초기화 실패인 경우 기본 응답 제공
        if "지식베이스 초기화 실패" in str(e) or "임베딩" in str(e):
            return {
                "query": request.query,
                "answer": "죄송합니다. 현재 지식베이스에 일시적인 문제가 있습니다. 기본 AI 응답을 제공합니다:\n\n" + 
                         "재무 관리에 대한 일반적인 조언을 드리겠습니다. 구체적인 질문이 있으시면 다시 시도해주세요.",
                "agent_type": "basic",
                "context_used": False,
                "error": "지식베이스 초기화 실패",
                "timestamp": datetime.now().isoformat()
            }
        
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

# ================================================
# 새로운 고급 기능 API 엔드포인트
# ================================================

@app.get("/financial-data/stock/{symbol}")
async def get_stock_data(symbol: str):
    """주식 데이터 조회 (비활성화)"""
    # 코스피/코스닥 제거로 인한 비활성화
    return {
        "symbol": symbol,
        "status": "disabled",
        "message": "주식 데이터 조회 기능이 비활성화되었습니다."
    }

@app.get("/financial-data/exchange-rate")
async def get_exchange_rate(from_currency: str = "USD", to_currency: str = "KRW"):
    """환율 정보 조회"""
    try:
        data = await financial_data.get_exchange_rate(from_currency, to_currency)
        if data:
            return data
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"환율 데이터를 찾을 수 없습니다: {from_currency}/{to_currency}"
            )
    except Exception as e:
        logger.error(f"환율 데이터 조회 실패: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"환율 데이터 조회 중 오류가 발생했습니다: {str(e)}"
        )

@app.get("/financial-data/economic-indicators")
async def get_economic_indicators():
    """경제 지표 조회"""
    try:
        data = await financial_data.get_economic_indicators()
        if data:
            return data
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="경제 지표 데이터를 찾을 수 없습니다."
            )
    except Exception as e:
        logger.error(f"경제 지표 조회 실패: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"경제 지표 조회 중 오류가 발생했습니다: {str(e)}"
        )

@app.post("/portfolio/simulate")
async def simulate_portfolio(request: Dict[str, Any]):
    """포트폴리오 시뮬레이션"""
    try:
        symbols = request.get("symbols", [])
        weights = request.get("weights", [])
        start_date = request.get("start_date", "2023-01-01")
        end_date = request.get("end_date")
        initial_investment = request.get("initial_investment", 10000000)
        
        if len(symbols) != len(weights):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="심볼과 가중치의 개수가 일치하지 않습니다."
            )
        
        result = portfolio_simulator.simulate_portfolio(
            symbols, weights, start_date, end_date, initial_investment
        )
        
        if "error" in result:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["error"]
            )
        
        return result
    except Exception as e:
        logger.error(f"포트폴리오 시뮬레이션 실패: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"포트폴리오 시뮬레이션 중 오류가 발생했습니다: {str(e)}"
        )

@app.post("/portfolio/efficient-frontier")
async def create_efficient_frontier(request: Dict[str, Any]):
    """효율적 프론티어 생성"""
    try:
        symbols = request.get("symbols", [])
        start_date = request.get("start_date", "2023-01-01")
        end_date = request.get("end_date")
        num_portfolios = request.get("num_portfolios", 1000)
        
        result = portfolio_simulator.create_efficient_frontier(
            symbols, start_date, end_date, num_portfolios
        )
        
        if "error" in result:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["error"]
            )
        
        return result
    except Exception as e:
        logger.error(f"효율적 프론티어 생성 실패: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"효율적 프론티어 생성 중 오류가 발생했습니다: {str(e)}"
        )

@app.post("/ai/sentiment-analysis")
async def analyze_sentiment(request: Dict[str, Any]):
    """시장 감정 분석"""
    try:
        text_data = request.get("text_data", [])
        
        if not text_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="분석할 텍스트 데이터가 필요합니다."
            )
        
        result = advanced_ai.analyze_market_sentiment(text_data)
        
        if "error" in result:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["error"]
            )
        
        return result
    except Exception as e:
        logger.error(f"감정 분석 실패: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"감정 분석 중 오류가 발생했습니다: {str(e)}"
        )

@app.get("/ai/market-prediction/{symbol}")
async def predict_market_trend(
    symbol: str,
    days: int = 30,
    confidence_level: float = 0.8
):
    """시장 트렌드 예측"""
    try:
        result = advanced_ai.predict_market_trend(symbol, days, confidence_level)
        
        if "error" in result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=result["error"]
            )
        
        return result
    except Exception as e:
        logger.error(f"시장 예측 실패: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"시장 예측 중 오류가 발생했습니다: {str(e)}"
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
    logger.info("[START] AI 재무관리 어드바이저 API 서버 시작 중...")
    
    # 기본 서버만 시작하고, 무거운 컴포넌트는 지연 로딩으로 처리
    logger.info("[FAST] 빠른 시작을 위해 지연 로딩 모드로 실행됩니다.")
    logger.info("[KB] 지식베이스, 멀티 에이전트, 라우터는 첫 요청 시 로드됩니다.")
    logger.info("[API] 회사 Azure OpenAI 서비스 연결은 첫 요청 시 수행됩니다.")
    
    # 전체 시작 시간 로깅
    total_elapsed = time.time() - total_start_time
    logger.info(f"[OK] 서버 시작 완료! 총 소요시간: {total_elapsed:.2f}초")
    logger.info("[TARGET] 이제 API 요청을 받을 준비가 되었습니다!")
    logger.info("[TIP] 첫 API 요청 시 Azure OpenAI 연결 및 컴포넌트들이 로드됩니다.")
    logger.info("[TIME] 첫 요청은 10-30초 정도 소요될 수 있습니다.")

# 종료 이벤트
@app.on_event("shutdown")
async def shutdown_event():
    """애플리케이션 종료 시 실행"""
    logger.info("[END] AI 재무관리 어드바이저 API 서버가 종료되었습니다.")

# 직접 실행 시
if __name__ == "__main__":
    uvicorn.run(
        "src.api.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level="info"
    )
