#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LangGraph 기반 고급 에이전트
LangGraph의 모든 기능을 완전히 반영한 고급 에이전트 시스템
"""

import os
import logging
import json
import requests
from typing import Dict, Any, List, Optional, Annotated, Literal
from datetime import datetime, timedelta

from langchain_openai import AzureChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage, ToolMessage
from langchain_core.tools import tool
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

# LangGraph 관련 임포트 (설치 후 사용 가능)
try:
    from langgraph.graph import StateGraph, MessagesState, START, END
    from langgraph.graph.message import add_messages
    from langgraph.prebuilt import ToolNode, create_react_agent
    from langgraph.checkpoint.memory import MemorySaver
    from langgraph.types import Command
    from typing_extensions import TypedDict
    LANGGRAPH_AVAILABLE = True
except ImportError:
    LANGGRAPH_AVAILABLE = False
    logging.warning("LangGraph가 설치되지 않았습니다. 일부 기능이 제한됩니다.")

logger = logging.getLogger(__name__)

# ================================================
# 1. 재무관리 전용 도구 정의
# ================================================

@tool
def get_user_financial_profile(user_id: str) -> Dict[str, Any]:
    """사용자의 재무 프로필을 조회합니다."""
    # 실제로는 데이터베이스에서 조회
    mock_data = {
        "user_id": user_id,
        "name": "김철수",
        "age": 35,
        "income": 60000000,
        "expenses": 35000000,
        "savings": 15000000,
        "risk_tolerance": "moderate",
        "investment_goals": ["은퇴준비", "자녀교육비"],
        "investment_portfolio": {
            "stocks": 8000000,
            "bonds": 4000000,
            "cash": 3000000
        }
    }
    return mock_data

@tool
def analyze_budget_health(income: float, expenses: float, savings: float) -> Dict[str, Any]:
    """예산 건강도를 분석합니다."""
    net_income = income - expenses
    savings_rate = (net_income / income * 100) if income > 0 else 0
    emergency_fund_months = (savings / expenses) if expenses > 0 else 0
    
    # 재무 건강도 점수 계산
    health_score = min(100, max(0, 
        savings_rate * 2 + 
        min(emergency_fund_months * 10, 40) +
        (20 if net_income > 0 else 0)
    ))
    
    status = "우수" if health_score >= 80 else "양호" if health_score >= 60 else "보통" if health_score >= 40 else "주의"
    
    return {
        "health_score": health_score,
        "status": status,
        "net_income": net_income,
        "savings_rate": savings_rate,
        "emergency_fund_months": emergency_fund_months,
        "recommendations": [
            "저축률을 20% 이상으로 유지하세요" if savings_rate < 20 else "좋은 저축률을 유지하고 있습니다",
            "비상금을 6개월치 생활비로 확보하세요" if emergency_fund_months < 6 else "적절한 비상금을 보유하고 있습니다"
        ]
    }

@tool
def get_investment_advice(age: int, risk_tolerance: str, investment_amount: float) -> Dict[str, Any]:
    """투자 조언을 제공합니다."""
    
    # 위험도별 자산 배분
    allocation_strategies = {
        "conservative": {"bonds": 70, "stocks": 20, "cash": 10},
        "moderate": {"bonds": 50, "stocks": 40, "cash": 10},
        "aggressive": {"bonds": 30, "stocks": 60, "cash": 10}
    }
    
    strategy = allocation_strategies.get(risk_tolerance, allocation_strategies["moderate"])
    
    # 나이 기반 조정 (100-나이 법칙)
    age_adjustment = max(0, (100 - age) / 100)
    final_allocation = {
        "bonds": strategy["bonds"] * age_adjustment,
        "stocks": strategy["stocks"] * (1 - age_adjustment * 0.3),
        "cash": strategy["cash"]
    }
    
    return {
        "allocation": final_allocation,
        "expected_return": 6.0 if risk_tolerance == "conservative" else 8.0 if risk_tolerance == "moderate" else 10.0,
        "risk_level": risk_tolerance,
        "recommendations": [
            "정기적인 포트폴리오 리밸런싱을 수행하세요",
            "분산 투자로 위험을 관리하세요",
            "장기 투자 관점을 유지하세요"
        ]
    }

@tool
def calculate_tax_optimization(income: float, deductions: Dict[str, float]) -> Dict[str, Any]:
    """세금 최적화를 계산합니다."""
    
    basic_deduction = 1500000
    total_deductions = basic_deduction + sum(deductions.values())
    taxable_income = max(0, income - total_deductions)
    
    # 세율 계산
    if taxable_income <= 12000000:
        tax_rate = 0.06
    elif taxable_income <= 46000000:
        tax_rate = 0.15
    elif taxable_income <= 88000000:
        tax_rate = 0.24
    else:
        tax_rate = 0.35
    
    tax_amount = taxable_income * tax_rate
    tax_savings = max(0, income - basic_deduction) * tax_rate - tax_amount
    
    return {
        "taxable_income": taxable_income,
        "tax_amount": tax_amount,
        "tax_savings": tax_savings,
        "effective_tax_rate": (tax_amount / income * 100) if income > 0 else 0,
        "optimization_tips": [
            "신용카드 공제를 최대한 활용하세요",
            "의료비 공제를 확인하세요",
            "보험료 공제를 활용하세요"
        ]
    }

@tool
def get_market_insights(symbols: List[str]) -> Dict[str, Any]:
    """시장 인사이트를 제공합니다."""
    
    market_data = {}
    for symbol in symbols:
        if symbol == "^KS11":  # KOSPI
            market_data[symbol] = {
                "name": "KOSPI",
                "current_price": 2500,
                "change_percent": 1.2,
                "trend": "상승",
                "analysis": "국내 경제 회복세와 함께 상승 추세"
            }
        elif symbol == "^GSPC":  # S&P 500
            market_data[symbol] = {
                "name": "S&P 500",
                "current_price": 4500,
                "change_percent": -0.5,
                "trend": "하락",
                "analysis": "인플레이션 우려로 조정세"
            }
        else:
            market_data[symbol] = {
                "name": symbol,
                "current_price": 100,
                "change_percent": 0.0,
                "trend": "보합",
                "analysis": "정보 부족"
            }
    
    return {
        "market_data": market_data,
        "overall_trend": "혼조세",
        "recommendation": "분산 투자와 정기 리밸런싱 권장",
        "timestamp": datetime.now().isoformat()
    }

# ================================================
# 2. LangGraph 기본 구조
# ================================================

class LangGraphBasicAgent:
    """LangGraph 기본 구조를 구현한 에이전트"""
    
    def __init__(self, agent_name: str = "재무관리 챗봇"):
        self.agent_name = agent_name
        self.llm = self._initialize_llm()
        
        if LANGGRAPH_AVAILABLE:
            self.graph = self._create_basic_graph()
        else:
            logger.warning("LangGraph가 설치되지 않아 기본 기능만 사용 가능합니다.")
    
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
    
    def _create_basic_graph(self):
        """기본 LangGraph 생성"""
        if not LANGGRAPH_AVAILABLE:
            return None
        
        # State 정의
        class State(TypedDict):
            messages: Annotated[list, add_messages]
        
        # 그래프 빌더 생성
        graph_builder = StateGraph(State)
        
        # 챗봇 노드 정의
        def chatbot(state: State):
            logger.info(f"챗봇 노드 실행: {state['messages']}")
            response = self.llm.invoke(state["messages"])
            return {"messages": [response]}
        
        # 노드와 엣지 추가
        graph_builder.add_node("chatbot", chatbot)
        graph_builder.add_edge(START, "chatbot")
        graph_builder.add_edge("chatbot", END)
        
        return graph_builder.compile()
    
    def chat(self, message: str) -> Dict[str, Any]:
        """기본 챗봇 기능"""
        if self.graph:
            try:
                result = self.graph.invoke({"messages": [("human", message)]})
                return {
                    "response": result["messages"][-1].content,
                    "method": "LangGraph Basic"
                }
            except Exception as e:
                logger.error(f"LangGraph 실행 실패: {e}")
                return {"error": str(e)}
        else:
            # LangGraph 없을 때 기본 응답
            try:
                response = self.llm.invoke([("human", message)])
                return {
                    "response": response.content,
                    "method": "Basic LLM"
                }
            except Exception as e:
                logger.error(f"LLM 실행 실패: {e}")
                return {"error": str(e)}

# ================================================
# 3. LangGraph Tool Agent
# ================================================

class LangGraphToolAgent:
    """LangGraph 기반 Tool Agent"""
    
    def __init__(self, agent_name: str = "재무관리 Tool Agent"):
        self.agent_name = agent_name
        self.llm = self._initialize_llm()
        self.tools = [
            get_user_financial_profile,
            analyze_budget_health,
            get_investment_advice,
            calculate_tax_optimization,
            get_market_insights
        ]
        
        if LANGGRAPH_AVAILABLE:
            self.workflow = self._create_tool_workflow()
        else:
            logger.warning("LangGraph가 설치되지 않아 Tool Agent 기능이 제한됩니다.")
    
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
    
    def _create_tool_workflow(self):
        """Tool Agent 워크플로우 생성"""
        if not LANGGRAPH_AVAILABLE:
            return None
        
        # Tool Node 생성
        tool_node = ToolNode(self.tools)
        model_with_tools = self.llm.bind_tools(self.tools)
        
        # 조건부 엣지 함수
        def should_continue(state: MessagesState):
            messages = state["messages"]
            last_message = messages[-1]
            if last_message.tool_calls:
                return "tools"
            return END
        
        # 모델 호출 함수
        def call_model(state: MessagesState):
            messages = state["messages"]
            response = model_with_tools.invoke(messages)
            return {"messages": [response]}
        
        # 워크플로우 생성
        workflow = StateGraph(MessagesState)
        workflow.add_node("agent", call_model)
        workflow.add_node("tools", tool_node)
        
        workflow.add_edge(START, "agent")
        workflow.add_conditional_edges("agent", should_continue, ["tools", END])
        workflow.add_edge("tools", "agent")
        
        return workflow.compile()
    
    def process_query(self, query: str) -> Dict[str, Any]:
        """Tool Agent로 질의 처리"""
        if self.workflow:
            try:
                result = self.workflow.invoke({"messages": [("human", query)]})
                return {
                    "response": result["messages"][-1].content,
                    "method": "LangGraph Tool Agent"
                }
            except Exception as e:
                logger.error(f"Tool Agent 실행 실패: {e}")
                return {"error": str(e)}
        else:
            return {"error": "LangGraph가 설치되지 않았습니다."}

# ================================================
# 4. LangGraph Multi Agent
# ================================================

class LangGraphMultiAgent:
    """LangGraph 기반 Multi Agent 시스템"""
    
    def __init__(self):
        self.llm = self._initialize_llm()
        self.members = ["budget_analyst", "investment_advisor", "tax_consultant", "market_analyst"]
        
        if LANGGRAPH_AVAILABLE:
            self.graph = self._create_multi_agent_graph()
        else:
            logger.warning("LangGraph가 설치되지 않아 Multi Agent 기능이 제한됩니다.")
    
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
    
    def _create_multi_agent_graph(self):
        """Multi Agent 그래프 생성"""
        if not LANGGRAPH_AVAILABLE:
            return None
        
        # Router 정의
        class Router(TypedDict):
            next: Literal["budget_analyst", "investment_advisor", "tax_consultant", "market_analyst", "FINISH"]
        
        class State(MessagesState):
            next: str
        
        # Supervisor 노드
        system_prompt = (
            "당신은 재무관리 전문가 팀의 수퍼바이저입니다. "
            f"다음 전문가들을 관리합니다: {self.members}. "
            "사용자의 요청에 따라 적절한 전문가를 선택하여 업무를 배분하세요. "
            "업무가 완료되면 FINISH로 응답하세요."
        )
        
        def supervisor_node(state: State) -> Command[Literal[*self.members, "__end__"]]:
            messages = [
                {"role": "system", "content": system_prompt},
            ] + state["messages"]
            response = self.llm.with_structured_output(Router).invoke(messages)
            goto = response["next"]
            if goto == "FINISH":
                goto = END
            
            return Command(goto=goto, update={"next": goto})
        
        # 각 전문가 에이전트 생성
        budget_agent = create_react_agent(
            self.llm, 
            tools=[get_user_financial_profile, analyze_budget_health], 
            prompt="당신은 예산 분석 전문가입니다. 사용자의 재무 상황을 분석하고 예산 관리 조언을 제공합니다."
        )
        
        investment_agent = create_react_agent(
            self.llm, 
            tools=[get_investment_advice], 
            prompt="당신은 투자 자문 전문가입니다. 사용자에게 적절한 투자 전략을 제시합니다."
        )
        
        tax_agent = create_react_agent(
            self.llm, 
            tools=[calculate_tax_optimization], 
            prompt="당신은 세무 전문가입니다. 사용자의 세금 최적화 방안을 제시합니다."
        )
        
        market_agent = create_react_agent(
            self.llm, 
            tools=[get_market_insights], 
            prompt="당신은 시장 분석 전문가입니다. 현재 시장 상황을 분석하고 인사이트를 제공합니다."
        )
        
        # 각 전문가 노드 정의
        def budget_node(state: State) -> Command[Literal["supervisor"]]:
            result = budget_agent.invoke(state)
            return Command(
                update={"messages": [HumanMessage(content=result["messages"][-1].content, name="budget_analyst")]},
                goto="supervisor",
            )
        
        def investment_node(state: State) -> Command[Literal["supervisor"]]:
            result = investment_agent.invoke(state)
            return Command(
                update={"messages": [HumanMessage(content=result["messages"][-1].content, name="investment_advisor")]},
                goto="supervisor",
            )
        
        def tax_node(state: State) -> Command[Literal["supervisor"]]:
            result = tax_agent.invoke(state)
            return Command(
                update={"messages": [HumanMessage(content=result["messages"][-1].content, name="tax_consultant")]},
                goto="supervisor",
            )
        
        def market_node(state: State) -> Command[Literal["supervisor"]]:
            result = market_agent.invoke(state)
            return Command(
                update={"messages": [HumanMessage(content=result["messages"][-1].content, name="market_analyst")]},
                goto="supervisor",
            )
        
        # 그래프 구성
        builder = StateGraph(State)
        builder.add_edge(START, "supervisor")
        builder.add_node("supervisor", supervisor_node)
        builder.add_node("budget_analyst", budget_node)
        builder.add_node("investment_advisor", investment_node)
        builder.add_node("tax_consultant", tax_node)
        builder.add_node("market_analyst", market_node)
        
        return builder.compile()
    
    def process_complex_query(self, query: str, thread_id: str = None) -> Dict[str, Any]:
        """Multi Agent로 복잡한 질의 처리"""
        if self.graph:
            try:
                config = {"configurable": {"thread_id": thread_id or "default"}} if thread_id else {}
                result = self.graph.invoke({"messages": [("human", query)]}, config=config)
                return {
                    "response": result["messages"][-1].content,
                    "method": "LangGraph Multi Agent",
                    "thread_id": thread_id
                }
            except Exception as e:
                logger.error(f"Multi Agent 실행 실패: {e}")
                return {"error": str(e)}
        else:
            return {"error": "LangGraph가 설치되지 않았습니다."}

# ================================================
# 5. 통합 LangGraph 에이전트
# ================================================

class IntegratedLangGraphAgent:
    """모든 LangGraph 기능을 통합한 에이전트"""
    
    def __init__(self):
        self.basic_agent = LangGraphBasicAgent()
        self.tool_agent = LangGraphToolAgent()
        self.multi_agent = LangGraphMultiAgent()
        
        # Memory 기능
        if LANGGRAPH_AVAILABLE:
            self.checkpointer = MemorySaver()
        else:
            self.checkpointer = None
        
        logger.info("✅ 통합 LangGraph 에이전트 초기화 완료")
    
    def basic_chat(self, message: str) -> Dict[str, Any]:
        """기본 챗봇 기능"""
        return self.basic_agent.chat(message)
    
    def tool_agent_query(self, query: str) -> Dict[str, Any]:
        """Tool Agent 질의"""
        return self.tool_agent.process_query(query)
    
    def multi_agent_query(self, query: str, thread_id: str = None) -> Dict[str, Any]:
        """Multi Agent 질의"""
        return self.multi_agent.process_complex_query(query, thread_id)
    
    def comprehensive_analysis(self, user_id: str, thread_id: str = None) -> Dict[str, Any]:
        """종합 재무 분석 (Multi Agent 활용)"""
        query = f"사용자 ID {user_id}의 종합적인 재무 분석을 수행해주세요. 예산 분석, 투자 조언, 세금 최적화, 시장 분석을 모두 포함해주세요."
        return self.multi_agent_query(query, thread_id)

# ================================================
# 6. 테스트 함수
# ================================================

def test_langgraph_agent():
    """LangGraph 에이전트 테스트"""
    print("🔧 LangGraph 에이전트 테스트 시작")
    print("=" * 50)
    
    # 통합 에이전트 생성
    agent = IntegratedLangGraphAgent()
    
    # 1. 기본 챗봇 테스트
    print("\n1️⃣ 기본 챗봇 테스트")
    result = agent.basic_chat("안녕하세요! 재무관리에 대해 궁금한 점이 있습니다.")
    print(f"결과: {result}")
    
    # 2. Tool Agent 테스트
    print("\n2️⃣ Tool Agent 테스트")
    result = agent.tool_agent_query("사용자 ID '12345'의 재무 프로필을 조회하고 예산 건강도를 분석해주세요.")
    print(f"결과: {result}")
    
    # 3. Multi Agent 테스트
    print("\n3️⃣ Multi Agent 테스트")
    result = agent.multi_agent_query("35세, 연소득 6000만원인 사용자의 종합적인 재무 상담을 받고 싶습니다.", "user_12345")
    print(f"결과: {result}")
    
    # 4. 종합 분석 테스트
    print("\n4️⃣ 종합 분석 테스트")
    result = agent.comprehensive_analysis("12345", "user_12345")
    print(f"결과: {result}")
    
    print("\n✅ LangGraph 에이전트 테스트 완료!")

if __name__ == "__main__":
    test_langgraph_agent()
