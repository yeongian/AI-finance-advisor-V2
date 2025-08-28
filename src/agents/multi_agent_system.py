"""
Multi Agent 시스템
LangChain과 LangGraph를 활용한 재무관리 전문 에이전트들
"""

import os
import logging
import time
from typing import Dict, Any, List, Optional
from datetime import datetime

from langchain.schema import HumanMessage, AIMessage
from langchain.memory import ConversationBufferMemory
from langchain_community.chat_models import AzureChatOpenAI
from langgraph.graph import StateGraph, END
# ToolExecutor는 사용하지 않으므로 제거
from langchain.tools import BaseTool
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder

from .budget_agent import BudgetAnalysisTool, ExpenseCategorizationTool, SavingsPlanTool
from .investment_agent import PortfolioAnalysisTool, InvestmentRecommendationTool, MarketAnalysisTool
from .tax_agent import TaxDeductionAnalysisTool, InvestmentTaxAnalysisTool, BusinessTaxAnalysisTool
from .retirement_agent import RetirementGoalCalculatorTool, PensionProductAnalysisTool, RetirementRoadmapTool
from ..rag.knowledge_base import KnowledgeBase

logger = logging.getLogger(__name__)

# AgentState 클래스 정의 (MultiAgentSystem보다 먼저 정의)
class AgentState:
    """에이전트 상태 클래스"""
    
    def __init__(self, query: str = "", user_data: Dict[str, Any] = None, 
                 context: str = "", results: Dict[str, Any] = None):
        self.query = query
        self.user_data = user_data or {}
        self.context = context
        self.results = results or {}

class MultiAgentSystem:
    """재무관리 Multi Agent 시스템"""
    
    def __init__(self):
        self.llm = None
        self.knowledge_base = None
        self.agents = {}
        self.memories = {}
        self.agent_executors = {}
        self.workflow = None
        self.is_initialized = False
        
    def initialize(self, knowledge_base: KnowledgeBase = None) -> bool:
        """Multi Agent 시스템 초기화"""
        total_start_time = time.time()
        try:
            logger.info("🤖 Multi Agent 시스템 초기화 시작...")
            
            # LLM 초기화
            llm_start_time = time.time()
            logger.info("🧠 LLM 초기화 중...")
            self.llm = AzureChatOpenAI(
                openai_api_key=os.getenv("AOAI_API_KEY"),
                openai_api_base=os.getenv("AOAI_ENDPOINT"),
                openai_api_version="2024-02-15-preview",
                deployment_name=os.getenv("AOAI_DEPLOY_GPT4O_MINI"),
                temperature=0.7
            )
            llm_elapsed = time.time() - llm_start_time
            logger.info(f"✅ LLM 초기화 완료: {llm_elapsed:.2f}초")
            
            # 지식베이스 설정
            self.knowledge_base = knowledge_base
            
            # 에이전트 초기화
            agent_start_time = time.time()
            logger.info("👥 에이전트 초기화 중...")
            self._initialize_agents()
            agent_elapsed = time.time() - agent_start_time
            logger.info(f"✅ 에이전트 초기화 완료: {agent_elapsed:.2f}초")
            
            # 워크플로우 생성
            workflow_start_time = time.time()
            logger.info("🔄 워크플로우 생성 중...")
            self._create_workflow()
            workflow_elapsed = time.time() - workflow_start_time
            logger.info(f"✅ 워크플로우 생성 완료: {workflow_elapsed:.2f}초")
            
            self.is_initialized = True
            total_elapsed = time.time() - total_start_time
            logger.info(f"🎉 Multi Agent 시스템 초기화 완료! 총 소요시간: {total_elapsed:.2f}초")
            return True
            
        except Exception as e:
            logger.error(f"❌ Multi Agent 시스템 초기화 실패: {e}")
            return False
    
    def _initialize_agents(self):
        """각 전문 에이전트 초기화"""
        try:
            # 예산 관리 에이전트
            budget_start_time = time.time()
            logger.info("💰 예산 관리 에이전트 초기화 중...")
            budget_tools = [
                BudgetAnalysisTool(),
                ExpenseCategorizationTool(),
                SavingsPlanTool()
            ]
            self.agents["budget"] = self._create_agent("budget", budget_tools)
            budget_elapsed = time.time() - budget_start_time
            logger.info(f"✅ 예산 관리 에이전트 완료: {budget_elapsed:.2f}초")
            
            # 투자 관리 에이전트
            investment_start_time = time.time()
            logger.info("📈 투자 관리 에이전트 초기화 중...")
            investment_tools = [
                PortfolioAnalysisTool(),
                InvestmentRecommendationTool(),
                MarketAnalysisTool()
            ]
            self.agents["investment"] = self._create_agent("investment", investment_tools)
            investment_elapsed = time.time() - investment_start_time
            logger.info(f"✅ 투자 관리 에이전트 완료: {investment_elapsed:.2f}초")
            
            # 세금 관리 에이전트
            tax_start_time = time.time()
            logger.info("💰 세금 관리 에이전트 초기화 중...")
            tax_tools = [
                TaxDeductionAnalysisTool(),
                InvestmentTaxAnalysisTool(),
                BusinessTaxAnalysisTool()
            ]
            self.agents["tax"] = self._create_agent("tax", tax_tools)
            tax_elapsed = time.time() - tax_start_time
            logger.info(f"✅ 세금 관리 에이전트 완료: {tax_elapsed:.2f}초")
            
            # 은퇴 관리 에이전트
            retirement_start_time = time.time()
            logger.info("👴 은퇴 관리 에이전트 초기화 중...")
            retirement_tools = [
                RetirementGoalCalculatorTool(),
                PensionProductAnalysisTool(),
                RetirementRoadmapTool()
            ]
            self.agents["retirement"] = self._create_agent("retirement", retirement_tools)
            retirement_elapsed = time.time() - retirement_start_time
            logger.info(f"✅ 은퇴 관리 에이전트 완료: {retirement_elapsed:.2f}초")
            
            logger.info(f"{len(self.agents)}개의 전문 에이전트 초기화 완료")
            
        except Exception as e:
            logger.error(f"에이전트 초기화 실패: {e}")
    
    def _create_agent(self, agent_type: str, tools: List[BaseTool]) -> AgentExecutor:
        """개별 에이전트 생성"""
        try:
            # 에이전트별 프롬프트 템플릿
            prompts = {
                "budget": """당신은 재무관리 전문가 중 예산 관리 전문가입니다.
사용자의 수입, 지출, 저축 상황을 분석하여 예산 관리 조언을 제공하세요.
항상 50/30/20 법칙과 비상금 준비 원칙을 고려하여 답변하세요.

{chat_history}
Human: {input}
{agent_scratchpad}""",
                
                "investment": """당신은 재무관리 전문가 중 투자 관리 전문가입니다.
사용자의 나이, 위험 성향, 투자 목표를 고려하여 포트폴리오 구성과 투자 전략을 제시하세요.
항상 분산 투자와 나이 기반 자산 배분 원칙을 고려하여 답변하세요.

{chat_history}
Human: {input}
{agent_scratchpad}""",
                
                "tax": """당신은 재무관리 전문가 중 세금 관리 전문가입니다.
사용자의 소득, 지출, 투자 상황을 분석하여 세금 절약 방안을 제시하세요.
소득공제, 보험료공제, 의료비공제 등 다양한 공제 항목을 고려하여 답변하세요.

{chat_history}
Human: {input}
{agent_scratchpad}""",
                
                "retirement": """당신은 재무관리 전문가 중 은퇴 계획 전문가입니다.
사용자의 나이, 현재 저축액, 은퇴 목표를 고려하여 은퇴 준비 전략을 제시하세요.
연금저축, IRP, 연금보험 등 다양한 은퇴 준비 방법을 고려하여 답변하세요.

{chat_history}
Human: {input}
{agent_scratchpad}"""
            }
            
            prompt = ChatPromptTemplate.from_messages([
                ("system", prompts.get(agent_type, "당신은 재무관리 전문가입니다.")),
                MessagesPlaceholder(variable_name="chat_history"),
                ("human", "{input}"),
                MessagesPlaceholder(variable_name="agent_scratchpad")
            ])
            
            # 에이전트 생성
            agent = create_openai_functions_agent(self.llm, tools, prompt)
            
            # 메모리 설정
            memory = ConversationBufferMemory(
                memory_key="chat_history",
                return_messages=True
            )
            
            # 에이전트 실행기 생성
            agent_executor = AgentExecutor(
                agent=agent,
                tools=tools,
                memory=memory,
                verbose=True,
                handle_parsing_errors=True
            )
            
            return agent_executor
            
        except Exception as e:
            logger.error(f"{agent_type} 에이전트 생성 실패: {e}")
            return None
    
    def _create_workflow(self):
        """에이전트 워크플로우 생성"""
        try:
            # 상태 그래프 생성
            workflow = StateGraph(AgentState)
            
            # 노드 추가
            workflow.add_node("budget_agent", self._run_budget_agent)
            workflow.add_node("investment_agent", self._run_investment_agent)
            workflow.add_node("tax_agent", self._run_tax_agent)
            workflow.add_node("retirement_agent", self._run_retirement_agent)
            workflow.add_node("coordinator", self._coordinate_agents)
            
            # 엣지 설정
            workflow.add_edge("budget_agent", "coordinator")
            workflow.add_edge("investment_agent", "coordinator")
            workflow.add_edge("tax_agent", "coordinator")
            workflow.add_edge("retirement_agent", "coordinator")
            workflow.add_edge("coordinator", END)
            
            # 시작 노드 설정
            workflow.set_entry_point("coordinator")
            
            self.workflow = workflow.compile()
            logger.info("에이전트 워크플로우 생성 완료")
            
        except Exception as e:
            logger.error(f"워크플로우 생성 실패: {e}")
    
    def process_query(self, query: str, user_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """사용자 쿼리 처리"""
        try:
            if not self.is_initialized:
                logger.warning("Multi Agent 시스템이 초기화되지 않았습니다.")
                return {"error": "시스템이 초기화되지 않았습니다."}
            
            # RAG를 통한 관련 컨텍스트 검색
            context = self.knowledge_base.get_relevant_context(query) if self.knowledge_base else ""
            
            # 쿼리 분석하여 적절한 에이전트 선택
            agent_type = self._classify_query(query)
            
            if agent_type in self.agents:
                # 특정 에이전트로 처리
                result = self.agents[agent_type].invoke({
                    "input": f"컨텍스트: {context}\n\n사용자 질문: {query}",
                    "user_data": user_data or {}
                })
                
                return {
                    "answer": result.get("output", ""),
                    "agent_type": agent_type,
                    "confidence": 0.9,
                    "context_used": bool(context)
                }
            else:
                # 워크플로우를 통한 종합 처리
                state = AgentState(
                    query=query,
                    user_data=user_data or {},
                    context=context,
                    results={}
                )
                
                final_state = self.workflow.invoke(state)
                
                return {
                    "answer": final_state.results.get("final_answer", ""),
                    "agent_type": "comprehensive",
                    "confidence": 0.8,
                    "context_used": bool(context),
                    "agent_results": final_state.results
                }
            
        except Exception as e:
            logger.error(f"쿼리 처리 실패: {e}")
            return {"error": f"처리 중 오류가 발생했습니다: {str(e)}"}
    
    def _classify_query(self, query: str) -> str:
        """쿼리 분류"""
        query_lower = query.lower()
        
        if any(word in query_lower for word in ["예산", "지출", "저축", "비상금"]):
            return "budget"
        elif any(word in query_lower for word in ["투자", "주식", "포트폴리오", "자산배분"]):
            return "investment"
        elif any(word in query_lower for word in ["세금", "공제", "연말정산"]):
            return "tax"
        elif any(word in query_lower for word in ["은퇴", "연금", "노후"]):
            return "retirement"
        else:
            return "comprehensive"
    
    def _run_budget_agent(self, state: AgentState) -> AgentState:
        """예산 에이전트 실행"""
        try:
            result = self.agents["budget"].invoke({
                "input": state.query,
                "user_data": state.user_data
            })
            state.results["budget"] = result.get("output", "")
            return state
        except Exception as e:
            logger.error(f"예산 에이전트 실행 실패: {e}")
            state.results["budget"] = "예산 분석 중 오류가 발생했습니다."
            return state
    
    def _run_investment_agent(self, state: AgentState) -> AgentState:
        """투자 에이전트 실행"""
        try:
            result = self.agents["investment"].invoke({
                "input": state.query,
                "user_data": state.user_data
            })
            state.results["investment"] = result.get("output", "")
            return state
        except Exception as e:
            logger.error(f"투자 에이전트 실행 실패: {e}")
            state.results["investment"] = "투자 분석 중 오류가 발생했습니다."
            return state
    
    def _run_tax_agent(self, state: AgentState) -> AgentState:
        """세금 에이전트 실행"""
        try:
            result = self.agents["tax"].invoke({
                "input": state.query,
                "user_data": state.user_data
            })
            state.results["tax"] = result.get("output", "")
            return state
        except Exception as e:
            logger.error(f"세금 에이전트 실행 실패: {e}")
            state.results["tax"] = "세금 분석 중 오류가 발생했습니다."
            return state
    
    def _run_retirement_agent(self, state: AgentState) -> AgentState:
        """은퇴 에이전트 실행"""
        try:
            result = self.agents["retirement"].invoke({
                "input": state.query,
                "user_data": state.user_data
            })
            state.results["retirement"] = result.get("output", "")
            return state
        except Exception as e:
            logger.error(f"은퇴 에이전트 실행 실패: {e}")
            state.results["retirement"] = "은퇴 분석 중 오류가 발생했습니다."
            return state
            
    def _coordinate_agents(self, state: AgentState) -> AgentState:
        """에이전트 조율"""
        try:
            # 모든 에이전트 결과를 종합
            final_answer = self._synthesize_results(state.results, state.query)
            state.results["final_answer"] = final_answer
            return state
        except Exception as e:
            logger.error(f"에이전트 조율 실패: {e}")
            state.results["final_answer"] = "종합 분석 중 오류가 발생했습니다."
            return state
    
    def _synthesize_results(self, results: Dict[str, str], query: str) -> str:
        """결과 종합"""
        try:
            synthesis_prompt = f"""
다음은 재무관리 전문 에이전트들의 분석 결과입니다. 
사용자의 질문에 대해 종합적이고 일관된 답변을 제공하세요.

사용자 질문: {query}

분석 결과:
- 예산 분석: {results.get('budget', 'N/A')}
- 투자 분석: {results.get('investment', 'N/A')}
- 세금 분석: {results.get('tax', 'N/A')}
- 은퇴 분석: {results.get('retirement', 'N/A')}

종합 답변:
"""
            
            response = self.llm.invoke(synthesis_prompt)
            return response.content
            
        except Exception as e:
            logger.error(f"결과 종합 실패: {e}")
            return "분석 결과를 종합하는 중 오류가 발생했습니다."
    
    def get_comprehensive_analysis(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """종합 재무 분석"""
        try:
            analysis_results = {}
            
            # 각 에이전트별 분석 수행
            for agent_type, agent in self.agents.items():
                analysis_query = self._get_analysis_query(agent_type, user_data)
                result = agent.invoke({
                    "input": analysis_query,
                    "user_data": user_data
                })
                analysis_results[agent_type] = result.get("output", "")
            
            return {
                "timestamp": datetime.now().isoformat(),
                "user_data": user_data,
                "budget_analysis": self._parse_budget_analysis(analysis_results.get("budget", "")),
                "investment_analysis": self._parse_investment_analysis(analysis_results.get("investment", "")),
                "tax_analysis": self._parse_tax_analysis(analysis_results.get("tax", "")),
                "retirement_analysis": self._parse_retirement_analysis(analysis_results.get("retirement", ""))
            }
                
        except Exception as e:
            logger.error(f"종합 분석 실패: {e}")
            return {"error": f"분석 중 오류가 발생했습니다: {str(e)}"}
    
    def _get_analysis_query(self, agent_type: str, user_data: Dict[str, Any]) -> str:
        """에이전트별 분석 쿼리 생성"""
        queries = {
            "budget": f"사용자의 예산 상황을 분석해주세요. 나이: {user_data.get('age', 0)}, 연소득: {user_data.get('income', 0)}, 연지출: {user_data.get('expenses', 0)}, 저축액: {user_data.get('savings', 0)}",
            "investment": f"사용자의 투자 포트폴리오를 분석해주세요. 나이: {user_data.get('age', 0)}, 위험 성향: {user_data.get('risk_tolerance', '보통')}",
            "tax": f"사용자의 세금 절약 방안을 분석해주세요. 나이: {user_data.get('age', 0)}, 연소득: {user_data.get('income', 0)}",
            "retirement": f"사용자의 은퇴 계획을 분석해주세요. 나이: {user_data.get('age', 0)}, 현재 저축액: {user_data.get('savings', 0)}"
        }
        return queries.get(agent_type, "")
    
    def _parse_budget_analysis(self, analysis: str) -> Dict[str, Any]:
        """예산 분석 결과 파싱"""
        # 실제 구현에서는 더 정교한 파싱 로직 필요
        return {
            "analysis": analysis,
            "recommendations": ["50/30/20 법칙을 적용하세요", "비상금을 3-6개월치 확보하세요"]
        }
    
    def _parse_investment_analysis(self, analysis: str) -> Dict[str, Any]:
        """투자 분석 결과 파싱"""
        return {
            "analysis": analysis,
            "recommendations": ["나이에 맞는 자산배분을 하세요", "분산 투자를 통해 위험을 줄이세요"]
        }
    
    def _parse_tax_analysis(self, analysis: str) -> Dict[str, Any]:
        """세금 분석 결과 파싱"""
        return {
            "analysis": analysis,
            "recommendations": ["신용카드 사용을 늘리세요", "보험료공제를 활용하세요"]
        }
    
    def _parse_retirement_analysis(self, analysis: str) -> Dict[str, Any]:
        """은퇴 분석 결과 파싱"""
        return {
            "analysis": analysis,
            "recommendations": ["연금저축을 시작하세요", "장기적인 관점에서 투자하세요"]
        }
    
    def get_agent_info(self) -> Dict[str, Any]:
        """에이전트 정보 조회"""
        return {
            "is_initialized": self.is_initialized,
            "agent_count": len(self.agents),
            "agents": list(self.agents.keys()),
            "workflow_exists": self.workflow is not None
        }
    
    def clear_all_memories(self):
        """모든 에이전트의 메모리 초기화"""
        try:
        for agent in self.agents.values():
                if hasattr(agent, 'memory'):
                    agent.memory.clear()
        logger.info("모든 에이전트의 메모리가 초기화되었습니다.")
        except Exception as e:
            logger.error(f"메모리 초기화 실패: {e}")
