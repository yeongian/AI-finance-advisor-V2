"""
AI Agent 기본 클래스
모든 AI Agent가 상속받는 기본 클래스입니다.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
from langchain.memory import ConversationBufferMemory
from ..core.config import config
from ..core.utils import setup_logging

class BaseAgent(ABC):
    """AI Agent 기본 클래스"""
    
    def __init__(self, agent_name: str, model_name: str = None):
        self.agent_name = agent_name
        self.model_name = model_name or config.DEFAULT_MODEL
        self.logger = setup_logging()
        
        # OpenAI 클라이언트 초기화
        openai_config = config.get_openai_config()
        self.llm = ChatOpenAI(
            model=self.model_name,
            **openai_config
        )
        
        # 대화 메모리
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )
        
        # 에이전트별 시스템 프롬프트
        self.system_prompt = self._get_system_prompt()
        
        self.logger.info(f"{self.agent_name} 에이전트가 초기화되었습니다.")
    
    @abstractmethod
    def _get_system_prompt(self) -> str:
        """에이전트별 시스템 프롬프트 반환"""
        pass
    
    @abstractmethod
    def process_query(self, user_query: str, user_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """사용자 질의 처리"""
        pass
    
    def _create_messages(self, user_query: str, context: str = "") -> List:
        """메시지 생성"""
        messages = [
            SystemMessage(content=self.system_prompt),
        ]
        
        # 컨텍스트가 있으면 추가
        if context:
            messages.append(SystemMessage(content=f"컨텍스트 정보: {context}"))
        
        # 사용자 질의 추가
        messages.append(HumanMessage(content=user_query))
        
        return messages
    
    def _get_response(self, messages: List) -> str:
        """LLM 응답 생성"""
        try:
            response = self.llm.invoke(messages)
            return response.content
        except Exception as e:
            self.logger.error(f"LLM 응답 생성 중 오류: {e}")
            return f"죄송합니다. 응답 생성 중 오류가 발생했습니다: {str(e)}"
    
    def _format_response(self, response: str, category: str = "general") -> Dict[str, Any]:
        """응답 포맷팅"""
        return {
            "agent_name": self.agent_name,
            "category": category,
            "response": response,
            "timestamp": self._get_timestamp(),
            "confidence": 0.9  # 기본 신뢰도
        }
    
    def _get_timestamp(self) -> str:
        """현재 타임스탬프 반환"""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def update_memory(self, user_query: str, response: str):
        """대화 메모리 업데이트"""
        self.memory.save_context(
            {"input": user_query},
            {"output": response}
        )
    
    def get_memory(self) -> List:
        """대화 메모리 반환"""
        return self.memory.chat_memory.messages
    
    def clear_memory(self):
        """대화 메모리 초기화"""
        self.memory.clear()
        self.logger.info(f"{self.agent_name} 에이전트의 메모리가 초기화되었습니다.")
