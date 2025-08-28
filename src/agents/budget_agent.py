"""
예산 관리 전문 에이전트
개인 예산 분석, 지출 관리, 저축 계획 등을 담당하는 AI 에이전트
"""

import logging
from typing import Dict, Any, List, Optional
import json
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta

from langchain.tools import BaseTool, tool
from langchain.schema import Document

from .base_agent import BaseAgent
from ..core.utils import format_currency, format_percentage, calculate_returns
from ..rag.knowledge_base import KnowledgeBase

logger = logging.getLogger(__name__)

class BudgetAnalysisTool(BaseTool):
    """예산 분석 도구"""
    
    name: str = "budget_analysis"
    description: str = "사용자의 수입, 지출, 저축 데이터를 분석하여 예산 현황을 파악합니다."
    
    def _run(self, user_data: str) -> str:
        """예산 분석 실행"""
        try:
            data = json.loads(user_data)
            
            income = data.get('income', 0)
            expenses = data.get('expenses', 0)
            savings = data.get('savings', 0)
            
            # 기본 지표 계산
            net_income = income - expenses
            savings_rate = (net_income / income * 100) if income > 0 else 0
            emergency_fund_months = (savings / expenses) if expenses > 0 else 0
            
            # 재무 건강도 점수 계산
            health_score = min(100, max(0, 
                savings_rate * 2 + 
                min(emergency_fund_months * 10, 40) +
                (20 if net_income > 0 else 0)
            ))
            
            analysis = {
                "net_income": net_income,
                "savings_rate": savings_rate,
                "emergency_fund_months": emergency_fund_months,
                "health_score": health_score,
                "recommendations": self._generate_recommendations(data)
            }
            
            return json.dumps(analysis, ensure_ascii=False, indent=2)
            
        except Exception as e:
            logger.error(f"예산 분석 실패: {e}")
            return json.dumps({"error": str(e)})
    
    def _generate_recommendations(self, data: Dict[str, Any]) -> List[str]:
        """추천사항 생성"""
        recommendations = []
        
        income = data.get('income', 0)
        expenses = data.get('expenses', 0)
        savings = data.get('savings', 0)
        
        if expenses > income * 0.8:
            recommendations.append("지출이 수입의 80%를 초과하고 있습니다. 불필요한 지출을 줄이세요.")
        
        if savings < expenses * 3:
            recommendations.append("비상금이 3개월치 생활비보다 적습니다. 저축을 늘리세요.")
        
        if income > 0 and (income - expenses) / income < 0.2:
            recommendations.append("저축률이 20% 미만입니다. 50/30/20 법칙을 적용해보세요.")
        
        return recommendations

class ExpenseCategorizationTool(BaseTool):
    """지출 분류 도구"""
    
    name: str = "expense_categorization"
    description: str = "지출 데이터를 카테고리별로 분류하고 분석합니다."
    
    def _run(self, expense_data: str) -> str:
        """지출 분류 실행"""
        try:
            data = json.loads(expense_data)
            monthly_expenses = data.get('monthly_expenses', {})
            
            # 카테고리별 분석
            categories = {
                "주거비": monthly_expenses.get('housing', 0),
                "식비": monthly_expenses.get('food', 0),
                "교통비": monthly_expenses.get('transportation', 0),
                "통신비": monthly_expenses.get('utilities', 0),
                "보험료": monthly_expenses.get('insurance', 0),
                "여가비": monthly_expenses.get('entertainment', 0),
                "기타": monthly_expenses.get('other', 0)
            }
            
            total_expenses = sum(categories.values())
            
            # 비율 계산
            ratios = {k: (v / total_expenses * 100) if total_expenses > 0 else 0 
                     for k, v in categories.items()}
            
            # 추천사항
            recommendations = []
            if ratios.get("주거비", 0) > 30:
                recommendations.append("주거비가 30%를 초과합니다. 주거비 절약을 고려하세요.")
            
            if ratios.get("여가비", 0) > 20:
                recommendations.append("여가비가 20%를 초과합니다. 여가비 지출을 조절하세요.")
            
            analysis = {
                "categories": categories,
                "ratios": ratios,
                "total_expenses": total_expenses,
                "recommendations": recommendations
            }
            
            return json.dumps(analysis, ensure_ascii=False, indent=2)
            
        except Exception as e:
            logger.error(f"지출 분류 실패: {e}")
            return json.dumps({"error": str(e)})

class SavingsPlanTool(BaseTool):
    """저축 계획 도구"""
    
    name: str = "savings_plan"
    description: str = "목표 기반 저축 계획을 수립합니다."
    
    def _run(self, plan_data: str) -> str:
        """저축 계획 수립"""
        try:
            data = json.loads(plan_data)
            
            current_savings = data.get('current_savings', 0)
            target_amount = data.get('target_amount', 0)
            target_months = data.get('target_months', 12)
            monthly_income = data.get('monthly_income', 0)
            monthly_expenses = data.get('monthly_expenses', 0)
            
            # 필요한 월 저축액 계산
            required_savings = (target_amount - current_savings) / target_months
            available_savings = monthly_income - monthly_expenses
            
            # 계획 수립
            plan = {
                "required_monthly_savings": required_savings,
                "available_savings": available_savings,
                "feasible": available_savings >= required_savings,
                "monthly_savings_plan": self._create_monthly_plan(data),
                "recommendations": self._generate_savings_recommendations(data)
            }
            
            return json.dumps(plan, ensure_ascii=False, indent=2)
            
        except Exception as e:
            logger.error(f"저축 계획 수립 실패: {e}")
            return json.dumps({"error": str(e)})
    
    def _create_monthly_plan(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """월별 저축 계획 생성"""
        monthly_income = data.get('monthly_income', 0)
        
        # 50/30/20 법칙 적용
        essential_expenses = monthly_income * 0.5  # 필수지출 50%
        discretionary_expenses = monthly_income * 0.3  # 선택지출 30%
        savings_investment = monthly_income * 0.2  # 저축/투자 20%
        
        return {
            "essential_expenses": essential_expenses,
            "discretionary_expenses": discretionary_expenses,
            "savings_investment": savings_investment,
            "description": "50/30/20 법칙에 따른 월별 예산 배분"
        }
    
    def _generate_savings_recommendations(self, data: Dict[str, Any]) -> List[str]:
        """저축 추천사항 생성"""
        recommendations = []
        
        monthly_income = data.get('monthly_income', 0)
        monthly_expenses = data.get('monthly_expenses', 0)
        
        if monthly_expenses > monthly_income * 0.8:
            recommendations.append("지출을 줄여서 저축 가능 금액을 늘리세요.")
        
        recommendations.append("자동이체를 설정하여 매월 일정 금액을 저축하세요.")
        recommendations.append("비상금을 먼저 확보한 후 목표 저축을 시작하세요.")
        
        return recommendations

class BudgetAgent(BaseAgent):
    """예산 관리 전문 에이전트"""
    
    def __init__(self):
        """예산 관리 에이전트 초기화"""
        super().__init__(
            agent_name="예산 관리 어드바이저",
            agent_role="개인 예산 분석, 지출 관리, 저축 계획 수립을 담당하는 전문가"
        )
        
        # 전문 도구 추가
        self.add_tool(BudgetAnalysisTool())
        self.add_tool(ExpenseCategorizationTool())
        self.add_tool(SavingsPlanTool())
        
        # 에이전트 실행기 초기화
        self.initialize_agent_executor()
    
    def _extend_system_prompt(self, base_prompt: str) -> str:
        """예산 관리 전문 프롬프트 확장"""
        specialized_prompt = """
예산 관리 전문가로서 다음 영역에 특화되어 있습니다:

1. 예산 분석
- 수입/지출 패턴 분석
- 저축률 계산 및 평가
- 재무 건강도 점수 산출
- 비상금 적정성 평가

2. 지출 관리
- 카테고리별 지출 분석
- 불필요한 지출 식별
- 지출 최적화 방안 제시
- 50/30/20 법칙 적용

3. 저축 계획
- 목표 기반 저축 계획 수립
- 월별 저축액 계산
- 저축 목표 달성 가능성 평가
- 자동 저축 시스템 구축

4. 재무 목표 설정
- 단기/중기/장기 목표 설정
- 목표 달성을 위한 로드맵 제공
- 우선순위 기반 목표 관리

답변 시 다음을 포함하세요:
- 구체적인 수치와 계산 과정
- 시각적 차트나 그래프 제안
- 실행 가능한 액션 플랜
- 정기적인 점검 방법
"""
        
        return base_prompt + specialized_prompt
    
    def analyze_budget(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """예산 분석 수행"""
        try:
            # 예산 분석 도구 실행
            analysis_result = self.tools[0]._run(json.dumps(user_data))
            analysis = json.loads(analysis_result)
            
            # 지출 분류 분석
            if 'monthly_expenses' in user_data:
                expense_result = self.tools[1]._run(json.dumps(user_data))
                expense_analysis = json.loads(expense_result)
                analysis['expense_analysis'] = expense_analysis
            
            return analysis
            
        except Exception as e:
            logger.error(f"예산 분석 실패: {e}")
            return {"error": str(e)}
    
    def create_savings_plan(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """저축 계획 수립"""
        try:
            plan_result = self.tools[2]._run(json.dumps(user_data))
            return json.loads(plan_result)
            
        except Exception as e:
            logger.error(f"저축 계획 수립 실패: {e}")
            return {"error": str(e)}
    
    def get_budget_recommendations(self, user_data: Dict[str, Any]) -> List[str]:
        """예산 관련 추천사항 생성"""
        recommendations = []
        
        # 기본 분석
        analysis = self.analyze_budget(user_data)
        if 'recommendations' in analysis:
            recommendations.extend(analysis['recommendations'])
        
        # 지출 분석
        if 'expense_analysis' in analysis:
            expense_recs = analysis['expense_analysis'].get('recommendations', [])
            recommendations.extend(expense_recs)
        
        # 저축 계획
        savings_plan = self.create_savings_plan(user_data)
        if 'recommendations' in savings_plan:
            recommendations.extend(savings_plan['recommendations'])
        
        return list(set(recommendations))  # 중복 제거
    
    def get_specialized_tools(self) -> List[BaseTool]:
        """전문 도구 목록 반환"""
        return [
            BudgetAnalysisTool(),
            ExpenseCategorizationTool(),
            SavingsPlanTool()
        ]
    
    def get_specialized_prompt(self) -> str:
        """전문 프롬프트 반환"""
        return """
당신은 예산 관리 전문가입니다. 다음 영역에서 전문성을 발휘하세요:

1. 예산 분석 및 진단
2. 지출 패턴 분석
3. 저축 계획 수립
4. 재무 목표 설정
5. 예산 최적화 방안 제시

항상 구체적이고 실행 가능한 조언을 제공하세요.
"""
