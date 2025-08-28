"""
기본 에이전트 클래스
모든 AI 에이전트의 기본이 되는 클래스
"""

import logging
from typing import Dict, Any, List, Optional
from abc import ABC, abstractmethod

from langchain_community.chat_models import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage, AIMessage
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.memory import ConversationBufferMemory
from langchain.tools import BaseTool
from langchain.agents import AgentExecutor, create_openai_functions_agent

from ..core.config import settings
from ..rag.knowledge_base import KnowledgeBase

logger = logging.getLogger(__name__)

class BaseAgent(ABC):
    """모든 AI 에이전트의 기본 클래스"""
    
    def __init__(self, agent_name: str, agent_role: str):
        """
        기본 에이전트 초기화
        
        Args:
            agent_name: 에이전트 이름
            agent_role: 에이전트 역할 설명
        """
        self.agent_name = agent_name
        self.agent_role = agent_role
        self.llm = self._initialize_llm()
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )
        self.tools: List[BaseTool] = []
        self.knowledge_base: Optional[KnowledgeBase] = None
        self.agent_executor: Optional[AgentExecutor] = None
        
        # 프롬프트 템플릿 초기화
        self.prompt_template = self._create_prompt_template()
        
    def _initialize_llm(self) -> ChatOpenAI:
        """LLM 초기화"""
        try:
            if settings.use_azure_openai:
                # Azure OpenAI 사용
                return ChatOpenAI(
                    model=settings.aoai_deploy_gpt4o_mini,
                    temperature=settings.temperature,
                    max_tokens=settings.max_tokens,
                    openai_api_key=settings.aoai_api_key,
                    openai_api_base=settings.aoai_endpoint,
                    openai_api_version="2024-02-15-preview",
                    deployment_name=settings.aoai_deploy_gpt4o_mini
                )
            else:
                # 일반 OpenAI 사용
                return ChatOpenAI(
                    model=settings.openai_model,
                    temperature=settings.temperature,
                    max_tokens=settings.max_tokens,
                    openai_api_key=settings.openai_api_key
                )
        except Exception as e:
            logger.error(f"LLM 초기화 실패: {e}")
            raise
    
    def _create_prompt_template(self) -> ChatPromptTemplate:
        """프롬프트 템플릿 생성"""
        system_prompt = self._get_system_prompt()
        
        return ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad")
        ])
    
    def _get_system_prompt(self) -> str:
        """시스템 프롬프트 생성"""
        base_prompt = f"""
당신은 {self.agent_name}입니다.

역할: {self.agent_role}

당신의 임무:
1. 사용자의 재무 관련 질문에 정확하고 유용한 답변을 제공하세요
2. 금융 지식베이스를 활용하여 최신 정보를 바탕으로 조언하세요
3. 사용자의 상황에 맞는 맞춤형 조언을 제공하세요
4. 복잡한 금융 개념을 쉽게 설명하세요
5. 실용적이고 실행 가능한 조언을 제공하세요

답변 형식:
- 명확하고 구조화된 답변을 제공하세요
- 필요시 단계별 설명을 사용하세요
- 구체적인 예시를 포함하세요
- 주의사항이나 리스크를 명시하세요

주의사항:
- 정확한 정보만을 제공하세요
- 투자 조언 시 리스크를 반드시 언급하세요
- 법적 조언은 제공하지 마세요
- 개인정보 보호를 위해 민감한 정보를 요구하지 마세요
"""
        
        # 하위 클래스에서 추가할 수 있도록 확장 가능하게 설계
        return self._extend_system_prompt(base_prompt)
    
    def _extend_system_prompt(self, base_prompt: str) -> str:
        """시스템 프롬프트 확장 (하위 클래스에서 오버라이드)"""
        return base_prompt
    
    def set_knowledge_base(self, knowledge_base: KnowledgeBase):
        """지식베이스 설정"""
        self.knowledge_base = knowledge_base
        logger.info(f"{self.agent_name}에 지식베이스가 설정되었습니다.")
    
    def add_tool(self, tool: BaseTool):
        """도구 추가"""
        self.tools.append(tool)
        logger.info(f"{self.agent_name}에 도구가 추가되었습니다: {tool.name}")
    
    def initialize_agent_executor(self):
        """에이전트 실행기 초기화"""
        if not self.tools:
            logger.warning(f"{self.agent_name}에 도구가 없습니다.")
            return
        
        try:
            agent = create_openai_functions_agent(
                llm=self.llm,
                tools=self.tools,
                prompt=self.prompt_template
            )
            
            self.agent_executor = AgentExecutor(
                agent=agent,
                tools=self.tools,
                memory=self.memory,
                verbose=True,
                max_iterations=settings.max_iterations
            )
            
            logger.info(f"{self.agent_name} 에이전트 실행기가 초기화되었습니다.")
            
        except Exception as e:
            logger.error(f"에이전트 실행기 초기화 실패: {e}")
            raise
    
    def get_context_from_knowledge_base(self, query: str) -> str:
        """지식베이스에서 컨텍스트 가져오기"""
        if not self.knowledge_base:
            return ""
        
        try:
            return self.knowledge_base.get_context_for_query(query)
        except Exception as e:
            logger.error(f"지식베이스 컨텍스트 가져오기 실패: {e}")
            return ""
    
    def process_query(self, query: str, user_context: Optional[Dict[str, Any]] = None) -> str:
        """
        사용자 쿼리 처리
        
        Args:
            query: 사용자 질문
            user_context: 사용자 컨텍스트 정보
            
        Returns:
            에이전트 응답
        """
        try:
            # 지식베이스에서 관련 정보 검색
            context = self.get_context_from_knowledge_base(query)
            
            # 사용자 컨텍스트와 결합
            enhanced_query = self._enhance_query_with_context(query, context, user_context)
            
            # 에이전트 실행기가 있으면 사용
            if self.agent_executor:
                response = self.agent_executor.invoke({
                    "input": enhanced_query
                })
                return response["output"]
            
            # 기본 LLM 응답
            messages = [
                SystemMessage(content=self._get_system_prompt()),
                HumanMessage(content=enhanced_query)
            ]
            
            response = self.llm.invoke(messages)
            return response.content
            
        except Exception as e:
            logger.error(f"쿼리 처리 실패: {e}")
            return f"죄송합니다. 처리 중 오류가 발생했습니다: {str(e)}"
    
    def _enhance_query_with_context(self, query: str, context: str, user_context: Optional[Dict[str, Any]] = None) -> str:
        """컨텍스트를 포함하여 쿼리 강화"""
        enhanced_query = query
        
        if context:
            enhanced_query += f"\n\n참고 정보:\n{context}"
        
        if user_context:
            user_info = self._format_user_context(user_context)
            enhanced_query += f"\n\n사용자 정보:\n{user_info}"
        
        return enhanced_query
    
    def _format_user_context(self, user_context: Dict[str, Any]) -> str:
        """사용자 컨텍스트 포맷팅"""
        formatted_parts = []
        
        if 'age' in user_context:
            formatted_parts.append(f"나이: {user_context['age']}세")
        
        if 'income' in user_context:
            formatted_parts.append(f"연소득: {user_context['income']:,}원")
        
        if 'expenses' in user_context:
            formatted_parts.append(f"연지출: {user_context['expenses']:,}원")
        
        if 'savings' in user_context:
            formatted_parts.append(f"저축액: {user_context['savings']:,}원")
        
        if 'risk_tolerance' in user_context:
            formatted_parts.append(f"위험 성향: {user_context['risk_tolerance']}")
        
        return ", ".join(formatted_parts)
    
    def get_agent_info(self) -> Dict[str, Any]:
        """에이전트 정보 반환"""
        return {
            "name": self.agent_name,
            "role": self.agent_role,
            "tools_count": len(self.tools),
            "has_knowledge_base": self.knowledge_base is not None,
            "has_agent_executor": self.agent_executor is not None,
            "memory_length": len(self.memory.chat_memory.messages) if self.memory else 0
        }
    
    def clear_memory(self):
        """대화 메모리 초기화"""
        if self.memory:
            self.memory.clear()
            logger.info(f"{self.agent_name}의 메모리가 초기화되었습니다.")
    
    @abstractmethod
    def get_specialized_tools(self) -> List[BaseTool]:
        """전문 도구 목록 반환 (하위 클래스에서 구현)"""
        pass
    
    @abstractmethod
    def get_specialized_prompt(self) -> str:
        """전문 프롬프트 반환 (하위 클래스에서 구현)"""
        pass
