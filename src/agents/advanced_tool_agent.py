#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
고급 Tool Calling & Agent Executor
LangChain의 Tool Calling & Agent Executor 패턴을 완전히 반영한 고급 에이전트
"""

import os
import logging
import json
import requests
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

from langchain_openai import AzureChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage, ToolMessage
from langchain_core.tools import tool
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain.memory import ConversationBufferMemory

logger = logging.getLogger(__name__)

# ================================================
# 1. @tool 데코레이터를 사용한 도구 정의
# ================================================

@tool
def get_user_financial_info(user_id: str) -> Dict[str, Any]:
    """사용자의 재무 정보를 조회합니다."""
    # 실제로는 데이터베이스나 API에서 조회
    mock_data = {
        "user_id": user_id,
        "name": "김철수",
        "age": 30,
        "income": 50000000,
        "expenses": 30000000,
        "savings": 10000000,
        "risk_tolerance": "moderate",
        "investment_portfolio": {
            "stocks": 5000000,
            "bonds": 3000000,
            "cash": 2000000
        }
    }
    return mock_data

@tool
def calculate_budget_analysis(income: float, expenses: float, savings: float) -> Dict[str, Any]:
    """예산 분석을 수행합니다."""
    net_income = income - expenses
    savings_rate = (net_income / income * 100) if income > 0 else 0
    emergency_fund_months = (savings / expenses) if expenses > 0 else 0
    
    # 재무 건강도 점수 계산
    health_score = min(100, max(0, 
        savings_rate * 2 + 
        min(emergency_fund_months * 10, 40) +
        (20 if net_income > 0 else 0)
    ))
    
    recommendations = []
    if expenses > income * 0.8:
        recommendations.append("지출이 수입의 80%를 초과하고 있습니다. 불필요한 지출을 줄이세요.")
    if savings < expenses * 3:
        recommendations.append("비상금이 3개월치 생활비보다 적습니다. 저축을 늘리세요.")
    if income > 0 and (income - expenses) / income < 0.2:
        recommendations.append("저축률이 20% 미만입니다. 50/30/20 법칙을 적용해보세요.")
    
    return {
        "net_income": net_income,
        "savings_rate": savings_rate,
        "emergency_fund_months": emergency_fund_months,
        "health_score": health_score,
        "recommendations": recommendations
    }

@tool
def get_investment_recommendation(age: int, risk_tolerance: str, investment_amount: float) -> Dict[str, Any]:
    """투자 권장사항을 생성합니다."""
    
    # 위험도별 자산 배분 전략
    allocation_strategies = {
        "conservative": {
            "bonds": 60,
            "stocks": 30,
            "cash": 10
        },
        "moderate": {
            "bonds": 40,
            "stocks": 50,
            "cash": 10
        },
        "aggressive": {
            "bonds": 20,
            "stocks": 70,
            "cash": 10
        }
    }
    
    # 나이 기반 조정 (100-나이 법칙)
    age_adjustment = max(0, (100 - age) / 100)
    strategy = allocation_strategies.get(risk_tolerance, allocation_strategies["moderate"])
    
    # 나이와 위험도를 고려한 최종 배분
    final_allocation = {
        "bonds": strategy["bonds"] * age_adjustment,
        "stocks": strategy["stocks"] * (1 - age_adjustment * 0.5),
        "cash": strategy["cash"]
    }
    
    # 투자 상품 추천
    recommendations = []
    if final_allocation["stocks"] > 30:
        recommendations.append("국내 주식형 ETF (예: KODEX 200)")
    if final_allocation["bonds"] > 20:
        recommendations.append("국채 ETF (예: KODEX 국채선물)")
    if final_allocation["cash"] > 5:
        recommendations.append("MMF 또는 단기 채권형 펀드")
    
    return {
        "allocation": final_allocation,
        "recommendations": recommendations,
        "expected_return": 5.5 if risk_tolerance == "conservative" else 7.2 if risk_tolerance == "moderate" else 9.0,
        "risk_level": risk_tolerance
    }

@tool
def calculate_tax_savings(income: float, deductions: Dict[str, float]) -> Dict[str, Any]:
    """세금 절약 효과를 계산합니다."""
    
    # 기본 공제
    basic_deduction = 1500000  # 기본공제 150만원
    
    # 추가 공제 계산
    total_deductions = basic_deduction
    for category, amount in deductions.items():
        total_deductions += amount
    
    # 과세표준 계산
    taxable_income = max(0, income - total_deductions)
    
    # 세율 계산 (간단한 누진세율)
    if taxable_income <= 12000000:
        tax_rate = 0.06
    elif taxable_income <= 46000000:
        tax_rate = 0.15
    elif taxable_income <= 88000000:
        tax_rate = 0.24
    elif taxable_income <= 150000000:
        tax_rate = 0.35
    elif taxable_income <= 300000000:
        tax_rate = 0.38
    else:
        tax_rate = 0.40
    
    tax_amount = taxable_income * tax_rate
    
    # 절약 효과 계산
    tax_without_deductions = max(0, income - basic_deduction) * tax_rate
    tax_savings = tax_without_deductions - tax_amount
    
    return {
        "taxable_income": taxable_income,
        "tax_amount": tax_amount,
        "tax_savings": tax_savings,
        "effective_tax_rate": (tax_amount / income * 100) if income > 0 else 0,
        "deductions_used": deductions
    }

@tool
def get_market_analysis(symbols: List[str]) -> Dict[str, Any]:
    """시장 분석 정보를 제공합니다."""
    
    # 실제로는 금융 API를 호출하지만, 여기서는 모의 데이터
    market_data = {}
    
    for symbol in symbols:
        if symbol == "^KS11":  # KOSPI
            market_data[symbol] = {
                "name": "KOSPI",
                "current_price": 2500,
                "change_percent": 1.2,
                "volume": 500000000,
                "trend": "상승",
                "analysis": "국내 경제 회복세와 함께 상승 추세를 보이고 있습니다."
            }
        elif symbol == "^GSPC":  # S&P 500
            market_data[symbol] = {
                "name": "S&P 500",
                "current_price": 4500,
                "change_percent": -0.5,
                "volume": 3000000000,
                "trend": "하락",
                "analysis": "인플레이션 우려로 인한 조정세를 보이고 있습니다."
            }
        else:
            market_data[symbol] = {
                "name": symbol,
                "current_price": 100,
                "change_percent": 0.0,
                "volume": 1000000,
                "trend": "보합",
                "analysis": "정보가 부족합니다."
            }
    
    return {
        "market_data": market_data,
        "overall_trend": "혼조세",
        "recommendation": "분산 투자와 정기 리밸런싱을 권장합니다.",
        "timestamp": datetime.now().isoformat()
    }

# ================================================
# 2. 고급 Tool Calling Agent 클래스
# ================================================

class AdvancedToolCallingAgent:
    """LangChain의 Tool Calling & Agent Executor 패턴을 완전히 반영한 고급 에이전트"""
    
    def __init__(self, agent_name: str = "재무관리 전문가"):
        """
        고급 Tool Calling Agent 초기화
        
        Args:
            agent_name: 에이전트 이름
        """
        self.agent_name = agent_name
        
        # 1. Azure OpenAI LLM 초기화
        self.llm = self._initialize_llm()
        
        # 2. 도구 정의
        self.tools = [
            get_user_financial_info,
            calculate_budget_analysis,
            get_investment_recommendation,
            calculate_tax_savings,
            get_market_analysis
        ]
        
        # 3. 도구와 LLM 연결
        self.llm_with_tools = self.llm.bind_tools(self.tools)
        
        # 4. 프롬프트 템플릿 생성
        self.prompt = self._create_prompt()
        
        # 5. Tool Calling Agent 생성
        self.agent = create_tool_calling_agent(self.llm, self.tools, self.prompt)
        
        # 6. Agent Executor 생성
        self.agent_executor = AgentExecutor(
            agent=self.agent,
            tools=self.tools,
            verbose=True,
            max_iterations=10,           # 최대 반복 횟수
            max_execution_time=30,       # 최대 실행 시간 (초)
            handle_parsing_errors=True,
        )
        
        # 7. 메모리 초기화 (수정됨)
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )
        
        logger.info(f"✅ {self.agent_name} 고급 Tool Calling Agent 초기화 완료")
    
    def _initialize_llm(self) -> AzureChatOpenAI:
        """Azure OpenAI LLM 초기화"""
        try:
            return AzureChatOpenAI(
                azure_endpoint=os.getenv("AOAI_ENDPOINT"),
                azure_deployment=os.getenv("AOAI_DEPLOY_GPT4O_MINI"),
                api_version="2024-10-21",
                api_key=os.getenv("AOAI_API_KEY"),
                temperature=0.7
            )
        except Exception as e:
            logger.error(f"LLM 초기화 실패: {e}")
            raise
    
    def _create_prompt(self) -> ChatPromptTemplate:
        """프롬프트 템플릿 생성"""
        return ChatPromptTemplate.from_messages([
            (
                "system",
                f"당신은 {self.agent_name}입니다. "
                "재무관리 전문가로서 사용자의 재무 상황을 분석하고 조언을 제공합니다. "
                "다음 도구들을 적절히 사용하여 정확한 분석을 수행하세요:\n"
                "- get_user_financial_info: 사용자 재무 정보 조회\n"
                "- calculate_budget_analysis: 예산 분석\n"
                "- get_investment_recommendation: 투자 권장사항\n"
                "- calculate_tax_savings: 세금 절약 효과 계산\n"
                "- get_market_analysis: 시장 분석\n"
                "도구 사용이 필요한 경우 반드시 사용하고, 결과를 바탕으로 구체적인 조언을 제공하세요."
            ),
            ("human", "{input}"),                                 # 사용자의 입력
            MessagesPlaceholder(variable_name="agent_scratchpad") # 에이전트가 임시로 사용하는 변수
        ])
    
    # ================================================
    # 3. 모든 기능 구현
    # ================================================
    
    def basic_tool_calling(self, query: str) -> Dict[str, Any]:
        """기본 Tool Calling"""
        try:
            # 도구와 연결된 LLM으로 질의 처리
            response = self.llm_with_tools.invoke(query)
            
            return {
                "query": query,
                "response": response.content,
                "tool_calls": response.tool_calls,
                "method": "Basic Tool Calling"
            }
        except Exception as e:
            logger.error(f"기본 Tool Calling 실패: {e}")
            return {"error": str(e)}
    
    def agent_executor_invoke(self, query: str) -> Dict[str, Any]:
        """Agent Executor를 사용한 질의 처리"""
        try:
            # Agent Executor로 질의 처리
            result = self.agent_executor.invoke({"input": query})
            
            return {
                "query": query,
                "response": result["output"],
                "intermediate_steps": result.get("intermediate_steps", []),
                "method": "Agent Executor"
            }
        except Exception as e:
            logger.error(f"Agent Executor 실행 실패: {e}")
            return {"error": str(e)}
    
    def comprehensive_financial_analysis(self, user_id: str) -> Dict[str, Any]:
        """종합 재무 분석 (모든 도구 활용) - 수정됨"""
        try:
            # 1. 사용자 정보 조회 (수정됨)
            user_info = get_user_financial_info.invoke({"user_id": user_id})
            
            # 2. 예산 분석 (수정됨)
            budget_analysis = calculate_budget_analysis.invoke({
                "income": user_info["income"],
                "expenses": user_info["expenses"],
                "savings": user_info["savings"]
            })
            
            # 3. 투자 권장사항 (수정됨)
            investment_rec = get_investment_recommendation.invoke({
                "age": user_info["age"],
                "risk_tolerance": user_info["risk_tolerance"],
                "investment_amount": user_info["savings"]
            })
            
            # 4. 세금 절약 효과 (수정됨)
            tax_savings = calculate_tax_savings.invoke({
                "income": user_info["income"],
                "deductions": {"신용카드": 1000000, "의료비": 500000, "보험료": 300000}
            })
            
            # 5. 시장 분석 (수정됨)
            market_analysis = get_market_analysis.invoke({"symbols": ["^KS11", "^GSPC"]})
            
            return {
                "user_info": user_info,
                "budget_analysis": budget_analysis,
                "investment_recommendation": investment_rec,
                "tax_savings": tax_savings,
                "market_analysis": market_analysis,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"종합 재무 분석 실패: {e}")
            return {"error": str(e)}
    
    def interactive_consultation(self, query: str, chat_history: List[Dict[str, str]] = None) -> Dict[str, Any]:
        """대화형 상담 (Agent Executor 활용)"""
        try:
            # 대화 히스토리 설정
            if chat_history:
                for message in chat_history:
                    if message["role"] == "user":
                        self.memory.chat_memory.add_user_message(message["content"])
                    elif message["role"] == "assistant":
                        self.memory.chat_memory.add_ai_message(message["content"])
            
            # Agent Executor로 상담 수행
            result = self.agent_executor.invoke({"input": query})
            
            return {
                "query": query,
                "response": result["output"],
                "chat_history": self.memory.chat_memory.messages,
                "method": "Interactive Consultation"
            }
        except Exception as e:
            logger.error(f"대화형 상담 실패: {e}")
            return {"error": str(e)}

# ================================================
# 4. 사용 예시 및 테스트
# ================================================

def test_advanced_tool_agent():
    """고급 Tool Calling Agent 테스트"""
    print("🔧 고급 Tool Calling Agent 테스트 시작")
    print("=" * 50)
    
    # 에이전트 생성
    agent = AdvancedToolCallingAgent("재무관리 전문가")
    
    # 1. 기본 Tool Calling 테스트
    print("\n1️⃣ 기본 Tool Calling 테스트")
    result = agent.basic_tool_calling("ID '12345' 사용자 정보를 조회해주세요.")
    print(f"결과: {result}")
    
    # 2. Agent Executor 테스트
    print("\n2️⃣ Agent Executor 테스트")
    result = agent.agent_executor_invoke("12345번 사용자 정보 좀 알려줘!")
    print(f"결과: {result}")
    
    # 3. 종합 재무 분석 테스트
    print("\n3️⃣ 종합 재무 분석 테스트")
    result = agent.comprehensive_financial_analysis("12345")
    print(f"분석 결과: {json.dumps(result, ensure_ascii=False, indent=2)}")
    
    # 4. 대화형 상담 테스트
    print("\n4️⃣ 대화형 상담 테스트")
    result = agent.interactive_consultation("안녕하세요! 재무 상담을 받고 싶습니다.")
    print(f"상담 결과: {result}")
    
    print("\n✅ 고급 Tool Calling Agent 테스트 완료!")

if __name__ == "__main__":
    test_advanced_tool_agent()
