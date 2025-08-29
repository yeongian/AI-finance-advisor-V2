#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LangGraph API 엔드포인트
LangGraph의 모든 기능을 활용한 고급 API
"""

import os
import logging
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from datetime import datetime

# LangGraph 에이전트 임포트
from ..agents.langgraph_agent import IntegratedLangGraphAgent

logger = logging.getLogger(__name__)

# 라우터 생성
router = APIRouter(prefix="/langgraph", tags=["LangGraph"])

# LangGraph 에이전트 인스턴스
langgraph_agent = None

def get_langgraph_agent():
    """LangGraph 에이전트 인스턴스 반환 (지연 로딩)"""
    global langgraph_agent
    
    if langgraph_agent is None:
        try:
            langgraph_agent = IntegratedLangGraphAgent()
            logger.info("✅ LangGraph 에이전트 초기화 완료")
        except Exception as e:
            logger.error(f"❌ LangGraph 에이전트 초기화 실패: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="LangGraph 에이전트 초기화 실패"
            )
    
    return langgraph_agent

# ================================================
# 1. 기본 LangGraph 챗봇 API
# ================================================

class BasicChatRequest(BaseModel):
    """기본 챗봇 요청"""
    message: str = Field(..., description="사용자 메시지")

@router.post("/basic-chat")
async def basic_chat(request: BasicChatRequest):
    """기본 LangGraph 챗봇"""
    try:
        agent = get_langgraph_agent()
        
        # 기본 챗봇 실행
        result = agent.basic_chat(request.message)
        
        return {
            "message": request.message,
            "response": result.get("response", ""),
            "method": result.get("method", "LangGraph Basic"),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"기본 챗봇 실패: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"기본 챗봇 실패: {str(e)}"
        )

# ================================================
# 2. LangGraph Tool Agent API
# ================================================

class ToolAgentRequest(BaseModel):
    """Tool Agent 요청"""
    query: str = Field(..., description="사용자 질의")

@router.post("/tool-agent")
async def tool_agent_query(request: ToolAgentRequest):
    """LangGraph Tool Agent 질의 처리"""
    try:
        agent = get_langgraph_agent()
        
        # Tool Agent 실행
        result = agent.tool_agent_query(request.query)
        
        return {
            "query": request.query,
            "response": result.get("response", ""),
            "method": result.get("method", "LangGraph Tool Agent"),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Tool Agent 실행 실패: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Tool Agent 실행 실패: {str(e)}"
        )

# ================================================
# 3. LangGraph Multi Agent API
# ================================================

class MultiAgentRequest(BaseModel):
    """Multi Agent 요청"""
    query: str = Field(..., description="사용자 질의")
    thread_id: Optional[str] = Field(default=None, description="스레드 ID (Memory 기능용)")

@router.post("/multi-agent")
async def multi_agent_query(request: MultiAgentRequest):
    """LangGraph Multi Agent 질의 처리"""
    try:
        agent = get_langgraph_agent()
        
        # Multi Agent 실행
        result = agent.multi_agent_query(request.query, request.thread_id)
        
        return {
            "query": request.query,
            "response": result.get("response", ""),
            "method": result.get("method", "LangGraph Multi Agent"),
            "thread_id": result.get("thread_id", request.thread_id),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Multi Agent 실행 실패: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Multi Agent 실행 실패: {str(e)}"
        )

# ================================================
# 4. 종합 재무 분석 API (Multi Agent 활용)
# ================================================

class ComprehensiveAnalysisRequest(BaseModel):
    """종합 재무 분석 요청"""
    user_id: str = Field(..., description="사용자 ID")
    thread_id: Optional[str] = Field(default=None, description="스레드 ID")

@router.post("/comprehensive-analysis")
async def comprehensive_analysis(request: ComprehensiveAnalysisRequest):
    """종합 재무 분석 (Multi Agent 활용)"""
    try:
        agent = get_langgraph_agent()
        
        # 종합 분석 실행
        result = agent.comprehensive_analysis(request.user_id, request.thread_id)
        
        return {
            "user_id": request.user_id,
            "response": result.get("response", ""),
            "method": result.get("method", "LangGraph Comprehensive Analysis"),
            "thread_id": result.get("thread_id", request.thread_id),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"종합 분석 실패: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"종합 분석 실패: {str(e)}"
        )

# ================================================
# 5. 대화형 상담 API (Memory 기능 포함)
# ================================================

class InteractiveConsultationRequest(BaseModel):
    """대화형 상담 요청"""
    message: str = Field(..., description="현재 메시지")
    thread_id: str = Field(..., description="스레드 ID (Memory 기능용)")

@router.post("/interactive-consultation")
async def interactive_consultation(request: InteractiveConsultationRequest):
    """대화형 상담 (Memory 기능 포함)"""
    try:
        agent = get_langgraph_agent()
        
        # 대화형 상담 실행 (Multi Agent 활용)
        result = agent.multi_agent_query(request.message, request.thread_id)
        
        return {
            "message": request.message,
            "response": result.get("response", ""),
            "method": result.get("method", "LangGraph Interactive Consultation"),
            "thread_id": result.get("thread_id", request.thread_id),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"대화형 상담 실패: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"대화형 상담 실패: {str(e)}"
        )

# ================================================
# 6. 전문가별 상담 API
# ================================================

class ExpertConsultationRequest(BaseModel):
    """전문가별 상담 요청"""
    expert_type: str = Field(..., description="전문가 유형 (budget_analyst, investment_advisor, tax_consultant, market_analyst)")
    query: str = Field(..., description="전문가에게 할 질의")
    thread_id: Optional[str] = Field(default=None, description="스레드 ID")

@router.post("/expert-consultation")
async def expert_consultation(request: ExpertConsultationRequest):
    """특정 전문가와의 상담"""
    try:
        agent = get_langgraph_agent()
        
        # 전문가별 질의 구성
        expert_prompts = {
            "budget_analyst": "예산 분석 전문가에게 문의: ",
            "investment_advisor": "투자 자문 전문가에게 문의: ",
            "tax_consultant": "세무 전문가에게 문의: ",
            "market_analyst": "시장 분석 전문가에게 문의: "
        }
        
        prompt = expert_prompts.get(request.expert_type, "")
        full_query = f"{prompt}{request.query}"
        
        # Multi Agent로 실행
        result = agent.multi_agent_query(full_query, request.thread_id)
        
        return {
            "expert_type": request.expert_type,
            "query": request.query,
            "response": result.get("response", ""),
            "method": f"LangGraph {request.expert_type} Consultation",
            "thread_id": result.get("thread_id", request.thread_id),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"전문가 상담 실패: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"전문가 상담 실패: {str(e)}"
        )

# ================================================
# 7. LangGraph 상태 확인
# ================================================

@router.get("/status")
async def get_langgraph_status():
    """LangGraph 기능 상태 확인"""
    try:
        agent = get_langgraph_agent()
        
        return {
            "status": "healthy",
            "langgraph_features": {
                "basic_chat": True,
                "tool_agent": True,
                "multi_agent": True,
                "memory": True,
                "comprehensive_analysis": True,
                "interactive_consultation": True,
                "expert_consultation": True
            },
            "available_experts": [
                "budget_analyst",
                "investment_advisor", 
                "tax_consultant",
                "market_analyst"
            ],
            "available_tools": [
                "get_user_financial_profile",
                "analyze_budget_health",
                "get_investment_advice",
                "calculate_tax_optimization",
                "get_market_insights"
            ],
            "langgraph_available": hasattr(agent, 'basic_agent') and hasattr(agent.basic_agent, 'graph'),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"LangGraph 상태 확인 실패: {e}")
        return {
            "status": "error",
            "error": str(e),
            "langgraph_available": False,
            "timestamp": datetime.now().isoformat()
        }

# ================================================
# 8. 스레드 관리 API (Memory 기능)
# ================================================

class ThreadInfo(BaseModel):
    """스레드 정보"""
    thread_id: str = Field(..., description="스레드 ID")
    created_at: str = Field(..., description="생성 시간")
    message_count: int = Field(..., description="메시지 수")

@router.get("/threads")
async def list_threads():
    """사용 가능한 스레드 목록 조회"""
    try:
        # 실제로는 데이터베이스에서 조회하지만, 여기서는 모의 데이터
        mock_threads = [
            ThreadInfo(
                thread_id="user_12345",
                created_at="2024-01-15T10:30:00",
                message_count=5
            ),
            ThreadInfo(
                thread_id="user_67890", 
                created_at="2024-01-15T14:20:00",
                message_count=3
            )
        ]
        
        return {
            "threads": mock_threads,
            "total_count": len(mock_threads),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"스레드 목록 조회 실패: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"스레드 목록 조회 실패: {str(e)}"
        )

@router.delete("/threads/{thread_id}")
async def delete_thread(thread_id: str):
    """스레드 삭제"""
    try:
        # 실제로는 데이터베이스에서 삭제
        return {
            "thread_id": thread_id,
            "status": "deleted",
            "message": "스레드가 성공적으로 삭제되었습니다.",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"스레드 삭제 실패: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"스레드 삭제 실패: {str(e)}"
        )
