#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
향상된 API 엔드포인트
LangChain의 고급 기능들을 활용한 새로운 API
"""

import os
import logging
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

# 향상된 에이전트 임포트
from ..agents.enhanced_agent import (
    EnhancedBudgetAgent, 
    EnhancedInvestmentAgent,
    FinancialAnalysis,
    InvestmentRecommendation,
    BudgetAnalysis
)

logger = logging.getLogger(__name__)

# 라우터 생성
router = APIRouter(prefix="/enhanced", tags=["Enhanced Features"])

# 향상된 에이전트 인스턴스들
budget_agent = None
investment_agent = None

def get_enhanced_agents():
    """향상된 에이전트 인스턴스 반환 (지연 로딩)"""
    global budget_agent, investment_agent
    
    if budget_agent is None:
        try:
            budget_agent = EnhancedBudgetAgent()
            logger.info("✅ 향상된 예산 에이전트 초기화 완료")
        except Exception as e:
            logger.error(f"❌ 향상된 예산 에이전트 초기화 실패: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="향상된 예산 에이전트 초기화 실패"
            )
    
    if investment_agent is None:
        try:
            investment_agent = EnhancedInvestmentAgent()
            logger.info("✅ 향상된 투자 에이전트 초기화 완료")
        except Exception as e:
            logger.error(f"❌ 향상된 투자 에이전트 초기화 실패: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="향상된 투자 에이전트 초기화 실패"
            )
    
    return budget_agent, investment_agent

# ================================================
# 1. LCEL 체인 기반 쿼리 처리
# ================================================

class LCELQueryRequest(BaseModel):
    """LCEL 체인 쿼리 요청"""
    query: str = Field(..., description="사용자 질문")
    user_data: Optional[Dict[str, Any]] = Field(default=None, description="사용자 데이터")

@router.post("/lcel-query")
async def process_lcel_query(request: LCELQueryRequest):
    """LCEL 체인을 사용한 쿼리 처리"""
    try:
        budget_agent, _ = get_enhanced_agents()
        
        # LCEL 체인 사용
        response = budget_agent.lcel_chain_invoke(request.query)
        
        return {
            "query": request.query,
            "response": response,
            "method": "LCEL Chain",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"LCEL 쿼리 처리 실패: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"LCEL 쿼리 처리 실패: {str(e)}"
        )

# ================================================
# 2. 구조화된 출력 분석
# ================================================

class StructuredAnalysisRequest(BaseModel):
    """구조화된 분석 요청"""
    analysis_type: str = Field(..., description="분석 유형 (financial, budget, investment)")
    user_data: Dict[str, Any] = Field(..., description="사용자 데이터")

@router.post("/structured-analysis")
async def get_structured_analysis(request: StructuredAnalysisRequest):
    """구조화된 출력을 사용한 분석"""
    try:
        budget_agent, investment_agent = get_enhanced_agents()
        
        if request.analysis_type == "financial":
            # 재무 상황 구조화 분석
            analysis = budget_agent.analyze_financial_situation(request.user_data)
            
            return {
                "analysis_type": "financial",
                "result": {
                    "analysis_type": analysis.analysis_type,
                    "summary": analysis.summary,
                    "recommendations": analysis.recommendations,
                    "risk_level": analysis.risk_level,
                    "confidence_score": analysis.confidence_score
                },
                "method": "Structured Output",
                "timestamp": datetime.now().isoformat()
            }
            
        elif request.analysis_type == "budget":
            # 예산 구조화 분석
            analysis = budget_agent.analyze_budget(request.user_data)
            
            return {
                "analysis_type": "budget",
                "result": {
                    "total_income": analysis.total_income,
                    "total_expenses": analysis.total_expenses,
                    "savings_rate": analysis.savings_rate,
                    "expense_categories": analysis.expense_categories,
                    "recommendations": analysis.recommendations
                },
                "method": "Structured Output",
                "timestamp": datetime.now().isoformat()
            }
            
        elif request.analysis_type == "investment":
            # 투자 권장사항 구조화 분석
            recommendation = investment_agent.create_portfolio_recommendation(request.user_data)
            
            return {
                "analysis_type": "investment",
                "result": {
                    "asset_type": recommendation.asset_type,
                    "allocation_percentage": recommendation.allocation_percentage,
                    "reasoning": recommendation.reasoning,
                    "expected_return": recommendation.expected_return,
                    "risk_level": recommendation.risk_level
                },
                "method": "Structured Output",
                "timestamp": datetime.now().isoformat()
            }
        
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"지원하지 않는 분석 유형: {request.analysis_type}"
            )
            
    except Exception as e:
        logger.error(f"구조화된 분석 실패: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"구조화된 분석 실패: {str(e)}"
        )

# ================================================
# 3. JSON 출력 파서 테스트
# ================================================

class JSONParserRequest(BaseModel):
    """JSON 파서 요청"""
    query: str = Field(..., description="분석할 쿼리")
    user_data: Optional[Dict[str, Any]] = Field(default=None, description="사용자 데이터")

@router.post("/json-parser")
async def test_json_parser(request: JSONParserRequest):
    """JSON 출력 파서 테스트"""
    try:
        budget_agent, _ = get_enhanced_agents()
        
        # JSON 출력 파서 사용
        result = budget_agent.json_output_invoke(request.query)
        
        return {
            "query": request.query,
            "result": result,
            "method": "JSON Output Parser",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"JSON 파서 테스트 실패: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"JSON 파서 테스트 실패: {str(e)}"
        )

# ================================================
# 4. 대화 히스토리 기반 채팅
# ================================================

class ChatWithHistoryRequest(BaseModel):
    """대화 히스토리 기반 채팅 요청"""
    message: str = Field(..., description="현재 메시지")
    chat_history: List[Dict[str, str]] = Field(..., description="대화 히스토리")
    user_data: Optional[Dict[str, Any]] = Field(default=None, description="사용자 데이터")

@router.post("/chat-with-history")
async def chat_with_history(request: ChatWithHistoryRequest):
    """대화 히스토리를 활용한 채팅"""
    try:
        budget_agent, _ = get_enhanced_agents()
        
        # 대화 히스토리와 함께 채팅
        response = budget_agent.chat_with_history(
            request.message, 
            request.chat_history
        )
        
        return {
            "message": request.message,
            "response": response,
            "chat_history": request.chat_history,
            "method": "Chat with History",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"대화 히스토리 채팅 실패: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"대화 히스토리 채팅 실패: {str(e)}"
        )

# ================================================
# 5. 멀티모달 분석 (향후 확장)
# ================================================

class MultimodalRequest(BaseModel):
    """멀티모달 분석 요청"""
    text: str = Field(..., description="텍스트 내용")
    image_url: Optional[str] = Field(default=None, description="이미지 URL")
    user_data: Optional[Dict[str, Any]] = Field(default=None, description="사용자 데이터")

@router.post("/multimodal-analysis")
async def multimodal_analysis(request: MultimodalRequest):
    """멀티모달 분석 (이미지 + 텍스트)"""
    try:
        budget_agent, _ = get_enhanced_agents()
        
        # 멀티모달 분석
        response = budget_agent.multimodal_analysis(
            request.text, 
            request.image_url
        )
        
        return {
            "text": request.text,
            "image_url": request.image_url,
            "response": response,
            "method": "Multimodal Analysis",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"멀티모달 분석 실패: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"멀티모달 분석 실패: {str(e)}"
        )

# ================================================
# 6. 향상된 기능 상태 확인
# ================================================

@router.get("/status")
async def get_enhanced_status():
    """향상된 기능 상태 확인"""
    try:
        budget_agent, investment_agent = get_enhanced_agents()
        
        return {
            "status": "healthy",
            "enhanced_features": {
                "lcel_chains": True,
                "structured_outputs": True,
                "json_parser": True,
                "chat_with_history": True,
                "multimodal_analysis": True
            },
            "agents": {
                "budget_agent": budget_agent is not None,
                "investment_agent": investment_agent is not None
            },
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"향상된 기능 상태 확인 실패: {e}")
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

# 필요한 import 추가
from datetime import datetime
