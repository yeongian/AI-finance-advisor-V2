#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
고급 Tool Calling & Agent Executor API 엔드포인트
LangChain의 Tool Calling & Agent Executor 기능을 활용한 고급 API
"""

import os
import logging
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

# 고급 Tool Calling Agent 임포트
from ..agents.advanced_tool_agent import AdvancedToolCallingAgent

logger = logging.getLogger(__name__)

# 라우터 생성
router = APIRouter(prefix="/advanced-tools", tags=["Advanced Tool Calling"])

# 고급 Tool Calling Agent 인스턴스
advanced_agent = None

def get_advanced_agent():
    """고급 Tool Calling Agent 인스턴스 반환 (지연 로딩)"""
    global advanced_agent
    
    if advanced_agent is None:
        try:
            advanced_agent = AdvancedToolCallingAgent("재무관리 전문가")
            logger.info("✅ 고급 Tool Calling Agent 초기화 완료")
        except Exception as e:
            logger.error(f"❌ 고급 Tool Calling Agent 초기화 실패: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="고급 Tool Calling Agent 초기화 실패"
            )
    
    return advanced_agent

# ================================================
# 1. 기본 Tool Calling API
# ================================================

class BasicToolCallingRequest(BaseModel):
    """기본 Tool Calling 요청"""
    query: str = Field(..., description="사용자 질문")

@router.post("/basic-tool-calling")
async def basic_tool_calling(request: BasicToolCallingRequest):
    """기본 Tool Calling 기능"""
    try:
        agent = get_advanced_agent()
        
        # 기본 Tool Calling 실행
        result = agent.basic_tool_calling(request.query)
        
        return {
            "query": request.query,
            "response": result.get("response", ""),
            "tool_calls": result.get("tool_calls", []),
            "method": result.get("method", "Basic Tool Calling"),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"기본 Tool Calling 실패: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"기본 Tool Calling 실패: {str(e)}"
        )

# ================================================
# 2. Agent Executor API
# ================================================

class AgentExecutorRequest(BaseModel):
    """Agent Executor 요청"""
    query: str = Field(..., description="사용자 질문")

@router.post("/agent-executor")
async def agent_executor_invoke(request: AgentExecutorRequest):
    """Agent Executor를 사용한 고급 질의 처리"""
    try:
        agent = get_advanced_agent()
        
        # Agent Executor 실행
        result = agent.agent_executor_invoke(request.query)
        
        return {
            "query": request.query,
            "response": result.get("response", ""),
            "intermediate_steps": result.get("intermediate_steps", []),
            "method": result.get("method", "Agent Executor"),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Agent Executor 실행 실패: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Agent Executor 실행 실패: {str(e)}"
        )

# ================================================
# 3. 종합 재무 분석 API
# ================================================

class ComprehensiveAnalysisRequest(BaseModel):
    """종합 재무 분석 요청"""
    user_id: str = Field(..., description="사용자 ID")

@router.post("/comprehensive-analysis")
async def comprehensive_financial_analysis(request: ComprehensiveAnalysisRequest):
    """종합 재무 분석 (모든 도구 활용)"""
    try:
        agent = get_advanced_agent()
        
        # 종합 재무 분석 실행
        result = agent.comprehensive_financial_analysis(request.user_id)
        
        return {
            "user_id": request.user_id,
            "analysis": result,
            "method": "Comprehensive Financial Analysis",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"종합 재무 분석 실패: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"종합 재무 분석 실패: {str(e)}"
        )

# ================================================
# 4. 대화형 상담 API
# ================================================

class InteractiveConsultationRequest(BaseModel):
    """대화형 상담 요청"""
    query: str = Field(..., description="현재 메시지")
    chat_history: Optional[List[Dict[str, str]]] = Field(default=None, description="대화 히스토리")

@router.post("/interactive-consultation")
async def interactive_consultation(request: InteractiveConsultationRequest):
    """대화형 상담 (Agent Executor 활용)"""
    try:
        agent = get_advanced_agent()
        
        # 대화형 상담 실행
        result = agent.interactive_consultation(request.query, request.chat_history)
        
        return {
            "query": request.query,
            "response": result.get("response", ""),
            "chat_history": result.get("chat_history", []),
            "method": result.get("method", "Interactive Consultation"),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"대화형 상담 실패: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"대화형 상담 실패: {str(e)}"
        )

# ================================================
# 5. 개별 도구 테스트 API
# ================================================

class ToolTestRequest(BaseModel):
    """도구 테스트 요청"""
    tool_name: str = Field(..., description="테스트할 도구 이름")
    parameters: Dict[str, Any] = Field(..., description="도구 파라미터")

@router.post("/tool-test")
async def test_individual_tool(request: ToolTestRequest):
    """개별 도구 테스트"""
    try:
        agent = get_advanced_agent()
        
        # 도구별 테스트 (수정됨)
        if request.tool_name == "get_user_financial_info":
            from ..agents.advanced_tool_agent import get_user_financial_info
            result = get_user_financial_info.invoke({"user_id": request.parameters.get("user_id", "")})
        elif request.tool_name == "calculate_budget_analysis":
            from ..agents.advanced_tool_agent import calculate_budget_analysis
            result = calculate_budget_analysis.invoke({
                "income": request.parameters.get("income", 0),
                "expenses": request.parameters.get("expenses", 0),
                "savings": request.parameters.get("savings", 0)
            })
        elif request.tool_name == "get_investment_recommendation":
            from ..agents.advanced_tool_agent import get_investment_recommendation
            result = get_investment_recommendation.invoke({
                "age": request.parameters.get("age", 30),
                "risk_tolerance": request.parameters.get("risk_tolerance", "moderate"),
                "investment_amount": request.parameters.get("investment_amount", 10000000)
            })
        elif request.tool_name == "calculate_tax_savings":
            from ..agents.advanced_tool_agent import calculate_tax_savings
            result = calculate_tax_savings.invoke({
                "income": request.parameters.get("income", 50000000),
                "deductions": request.parameters.get("deductions", {})
            })
        elif request.tool_name == "get_market_analysis":
            from ..agents.advanced_tool_agent import get_market_analysis
            result = get_market_analysis.invoke({"symbols": request.parameters.get("symbols", ["^KS11"])})
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"지원하지 않는 도구: {request.tool_name}"
            )
        
        return {
            "tool_name": request.tool_name,
            "parameters": request.parameters,
            "result": result,
            "method": "Individual Tool Test",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"도구 테스트 실패: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"도구 테스트 실패: {str(e)}"
        )

# ================================================
# 6. 고급 기능 상태 확인
# ================================================

@router.get("/status")
async def get_advanced_tool_status():
    """고급 Tool Calling 기능 상태 확인"""
    try:
        agent = get_advanced_agent()
        
        return {
            "status": "healthy",
            "advanced_features": {
                "basic_tool_calling": True,
                "agent_executor": True,
                "comprehensive_analysis": True,
                "interactive_consultation": True,
                "individual_tool_test": True
            },
            "available_tools": [
                "get_user_financial_info",
                "calculate_budget_analysis", 
                "get_investment_recommendation",
                "calculate_tax_savings",
                "get_market_analysis"
            ],
            "agent": {
                "name": agent.agent_name,
                "initialized": agent is not None
            },
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"고급 Tool Calling 상태 확인 실패: {e}")
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

# 필요한 import 추가
from datetime import datetime
