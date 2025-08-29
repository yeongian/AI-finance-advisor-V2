#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
향상된 에이전트 클래스
LangChain의 모든 고급 기능을 반영한 고도화된 에이전트
"""

import os
import logging
from typing import Dict, Any, List, Optional, Union
from abc import ABC, abstractmethod
from pydantic import BaseModel, Field

from langchain_core.messages import HumanMessage, SystemMessage, AIMessage, ToolMessage
from langchain_openai import AzureChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser
from langchain.memory import ConversationBufferMemory
from langchain.tools import BaseTool
from langchain.agents import AgentExecutor, create_openai_functions_agent

logger = logging.getLogger(__name__)

# ================================================
# 1. Structured Outputs를 위한 Pydantic 모델들
# ================================================

class FinancialAnalysis(BaseModel):
    """재무 분석 결과 구조화 모델"""
    analysis_type: str = Field(description="분석 유형")
    summary: str = Field(description="분석 요약")
    recommendations: List[str] = Field(description="권장사항 목록")
    risk_level: str = Field(description="위험도 수준")
    confidence_score: float = Field(description="신뢰도 점수 (0-1)")

class InvestmentRecommendation(BaseModel):
    """투자 권장사항 구조화 모델"""
    asset_type: str = Field(description="자산 유형")
    allocation_percentage: float = Field(description="배분 비율 (%)")
    reasoning: str = Field(description="권장 이유")
    expected_return: float = Field(description="예상 수익률 (%)")
    risk_level: str = Field(description="위험도")

class BudgetAnalysis(BaseModel):
    """예산 분석 구조화 모델"""
    total_income: float = Field(description="총 수입")
    total_expenses: float = Field(description="총 지출")
    savings_rate: float = Field(description="저축률 (%)")
    expense_categories: Dict[str, float] = Field(description="지출 카테고리별 금액")
    recommendations: List[str] = Field(description="개선 권장사항")

# ================================================
# 2. 향상된 에이전트 클래스
# ================================================

class EnhancedAgent(ABC):
    """LangChain의 모든 고급 기능을 반영한 향상된 에이전트"""
    
    def __init__(self, agent_name: str, agent_role: str):
        """
        향상된 에이전트 초기화
        
        Args:
            agent_name: 에이전트 이름
            agent_role: 에이전트 역할 설명
        """
        self.agent_name = agent_name
        self.agent_role = agent_role
        
        # 1. Azure OpenAI LLM 초기화
        self.llm = self._initialize_llm()
        
        # 2. 구조화된 출력을 위한 LLM
        self.structured_llm = self.llm.with_structured_output(FinancialAnalysis)
        
        # 3. 메모리 초기화
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )
        
        # 4. 도구 및 실행기
        self.tools: List[BaseTool] = []
        self.agent_executor: Optional[AgentExecutor] = None
        
        # 5. LCEL 체인들 초기화
        self._initialize_chains()
        
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
    
    def _initialize_chains(self):
        """LCEL 체인들 초기화"""
        # 1. 기본 프롬프트 템플릿
        self.basic_prompt = ChatPromptTemplate.from_messages([
            ("system", f"당신은 {self.agent_name}입니다. {self.agent_role}"),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}")
        ])
        
        # 2. 구조화된 프롬프트 템플릿
        self.structured_prompt = ChatPromptTemplate.from_messages([
            ("system", f"당신은 {self.agent_name}입니다. {self.agent_role} 구조화된 분석을 제공하세요."),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}")
        ])
        
        # 3. LCEL 체인들 생성
        self.basic_chain = self.basic_prompt | self.llm | StrOutputParser()
        self.structured_chain = self.structured_prompt | self.structured_llm
        
        # 4. JSON 출력 파서 체인
        self.json_parser = JsonOutputParser(pydantic_object=FinancialAnalysis)
        self.json_prompt = ChatPromptTemplate(
            template="재무 분석을 수행하세요.\n{format_instructions}\n{input}\n",
            input_variables=["input"],
            partial_variables={"format_instructions": self.json_parser.get_format_instructions()}
        )
        self.json_chain = self.json_prompt | self.llm | self.json_parser
    
    # ================================================
    # 3. 모든 고급 기능 구현
    # ================================================
    
    def basic_chat_completion(self, message: str) -> str:
        """기본 Chat Completion"""
        try:
            messages = [
                ("system", f"당신은 {self.agent_name}입니다."),
                ("human", message),
            ]
            response = self.llm.invoke(messages)
            return response.content
        except Exception as e:
            logger.error(f"기본 Chat Completion 실패: {e}")
            return f"오류가 발생했습니다: {e}"
    
    def lcel_chain_invoke(self, input_text: str) -> str:
        """LCEL 체인 사용"""
        try:
            return self.basic_chain.invoke({"input": input_text})
        except Exception as e:
            logger.error(f"LCEL 체인 실행 실패: {e}")
            return f"오류가 발생했습니다: {e}"
    
    def structured_output_invoke(self, input_text: str) -> FinancialAnalysis:
        """구조화된 출력"""
        try:
            return self.structured_chain.invoke({"input": input_text})
        except Exception as e:
            logger.error(f"구조화된 출력 실패: {e}")
            return FinancialAnalysis(
                analysis_type="error",
                summary=f"오류 발생: {e}",
                recommendations=[],
                risk_level="unknown",
                confidence_score=0.0
            )
    
    def json_output_invoke(self, input_text: str) -> Dict[str, Any]:
        """JSON 출력 파서"""
        try:
            return self.json_chain.invoke({"input": input_text})
        except Exception as e:
            logger.error(f"JSON 출력 파서 실패: {e}")
            return {"error": str(e)}
    
    def chat_with_history(self, input_text: str, chat_history: List[Dict[str, str]]) -> str:
        """대화 히스토리와 함께 채팅"""
        try:
            # MessagesPlaceholder를 활용한 동적 대화 히스토리
            chat_prompt = ChatPromptTemplate.from_messages([
                ("system", f"당신은 {self.agent_name}입니다."),
                MessagesPlaceholder(variable_name="chat_history"),
                ("human", "{input}")
            ])
            
            chain = chat_prompt | self.llm | StrOutputParser()
            return chain.invoke({
                "chat_history": chat_history,
                "input": input_text
            })
        except Exception as e:
            logger.error(f"대화 히스토리 채팅 실패: {e}")
            return f"오류가 발생했습니다: {e}"
    
    def multimodal_analysis(self, text: str, image_url: str = None) -> str:
        """멀티모달 분석"""
        try:
            if image_url:
                # 이미지가 있는 경우 멀티모달 메시지 생성
                message = HumanMessage(
                    content=[
                        {"type": "text", "text": text},
                        {"type": "image_url", "image_url": {"url": image_url}},
                    ],
                )
                response = self.llm.invoke([message])
                return response.content
            else:
                # 텍스트만 있는 경우
                return self.basic_chat_completion(text)
        except Exception as e:
            logger.error(f"멀티모달 분석 실패: {e}")
            return f"오류가 발생했습니다: {e}"
    
    # ================================================
    # 4. 재무관리 특화 기능들
    # ================================================
    
    def analyze_financial_situation(self, user_data: Dict[str, Any]) -> FinancialAnalysis:
        """재무 상황 구조화 분석"""
        input_text = f"""
        사용자 재무 상황을 분석해주세요:
        나이: {user_data.get('age', 'N/A')}
        소득: {user_data.get('income', 'N/A')}
        지출: {user_data.get('expenses', 'N/A')}
        저축: {user_data.get('savings', 'N/A')}
        위험 성향: {user_data.get('risk_tolerance', 'N/A')}
        """
        return self.structured_output_invoke(input_text)
    
    def get_investment_recommendations(self, user_data: Dict[str, Any]) -> InvestmentRecommendation:
        """투자 권장사항 구조화 출력"""
        structured_llm = self.llm.with_structured_output(InvestmentRecommendation)
        
        input_text = f"""
        사용자 상황에 맞는 투자 권장사항을 제공해주세요:
        나이: {user_data.get('age', 'N/A')}
        위험 성향: {user_data.get('risk_tolerance', 'N/A')}
        투자 가능 금액: {user_data.get('savings', 'N/A')}
        """
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", f"당신은 {self.agent_name}입니다. 투자 권장사항을 제공하세요."),
            ("human", input_text)
        ])
        
        chain = prompt | structured_llm
        return chain.invoke({"input": input_text})
    
    def analyze_budget(self, user_data: Dict[str, Any]) -> BudgetAnalysis:
        """예산 분석 구조화 출력"""
        structured_llm = self.llm.with_structured_output(BudgetAnalysis)
        
        input_text = f"""
        사용자의 예산을 분석해주세요:
        소득: {user_data.get('income', 'N/A')}
        지출: {user_data.get('expenses', 'N/A')}
        월별 지출: {user_data.get('monthly_expenses', 'N/A')}
        """
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", f"당신은 {self.agent_name}입니다. 예산 분석을 제공하세요."),
            ("human", input_text)
        ])
        
        chain = prompt | structured_llm
        return chain.invoke({"input": input_text})

# ================================================
# 5. 구체적인 에이전트 구현 예시
# ================================================

class EnhancedBudgetAgent(EnhancedAgent):
    """향상된 예산 관리 에이전트"""
    
    def __init__(self):
        super().__init__(
            agent_name="예산 관리 전문가",
            agent_role="개인 및 가계 예산 분석, 지출 최적화, 저축 계획 수립"
        )
    
    def analyze_monthly_expenses(self, expenses: Dict[str, float]) -> BudgetAnalysis:
        """월별 지출 분석"""
        input_text = f"다음 월별 지출을 분석해주세요: {expenses}"
        return self.analyze_budget({"monthly_expenses": expenses})

class EnhancedInvestmentAgent(EnhancedAgent):
    """향상된 투자 관리 에이전트"""
    
    def __init__(self):
        super().__init__(
            agent_name="투자 관리 전문가",
            agent_role="포트폴리오 분석, 투자 전략 수립, 리스크 관리"
        )
    
    def create_portfolio_recommendation(self, user_data: Dict[str, Any]) -> InvestmentRecommendation:
        """포트폴리오 권장사항 생성"""
        return self.get_investment_recommendations(user_data)

# ================================================
# 6. 사용 예시
# ================================================

def test_enhanced_agent():
    """향상된 에이전트 테스트"""
    print("🔧 향상된 에이전트 테스트 시작")
    print("=" * 50)
    
    # 에이전트 생성
    budget_agent = EnhancedBudgetAgent()
    
    # 1. 기본 Chat Completion 테스트
    print("\n1️⃣ 기본 Chat Completion 테스트")
    response = budget_agent.basic_chat_completion("안녕하세요! 예산 관리에 대해 조언해주세요.")
    print(f"응답: {response}")
    
    # 2. LCEL 체인 테스트
    print("\n2️⃣ LCEL 체인 테스트")
    response = budget_agent.lcel_chain_invoke("월급 500만원, 지출 300만원일 때 예산 관리는?")
    print(f"응답: {response}")
    
    # 3. 구조화된 출력 테스트
    print("\n3️⃣ 구조화된 출력 테스트")
    user_data = {
        "age": 30,
        "income": 50000000,
        "expenses": 30000000,
        "savings": 10000000,
        "risk_tolerance": "moderate"
    }
    analysis = budget_agent.analyze_financial_situation(user_data)
    print(f"분석 결과: {analysis}")
    
    # 4. JSON 출력 파서 테스트
    print("\n4️⃣ JSON 출력 파서 테스트")
    json_result = budget_agent.json_output_invoke("재무 상황을 분석해주세요.")
    print(f"JSON 결과: {json_result}")
    
    # 5. 대화 히스토리 테스트
    print("\n5️⃣ 대화 히스토리 테스트")
    chat_history = [
        {"role": "human", "content": "안녕하세요!"},
        {"role": "ai", "content": "안녕하세요! 예산 관리에 도움이 필요하신가요?"}
    ]
    response = budget_agent.chat_with_history("예산 관리는 어떻게 해야 할까요?", chat_history)
    print(f"대화 응답: {response}")
    
    print("\n✅ 향상된 에이전트 테스트 완료!")

if __name__ == "__main__":
    test_enhanced_agent()
