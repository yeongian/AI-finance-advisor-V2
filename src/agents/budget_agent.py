"""
예산 분석 및 추천 AI Agent
사용자의 소득/지출 패턴을 분석하고 예산 최적화 조언을 제공합니다.
"""

from typing import Dict, Any, List
from .base_agent import BaseAgent
from ..core.utils import format_currency, calculate_basic_metrics, validate_user_input

class BudgetAgent(BaseAgent):
    """예산 분석 및 추천 AI Agent"""
    
    def __init__(self):
        super().__init__("Budget Advisor", "gpt-4o-mini")
    
    def _get_system_prompt(self) -> str:
        return """당신은 전문적인 개인 재무 관리 어드바이저입니다. 
특히 예산 관리와 지출 최적화에 전문성을 가지고 있습니다.

당신의 역할:
1. 사용자의 소득과 지출 패턴을 분석하여 예산 최적화 방안을 제시
2. 카테고리별 지출 분석을 통한 절약 포인트 발견
3. 실현 가능한 예산 계획 수립 지원
4. 재무 목표 달성을 위한 단계별 가이드 제공

답변 시 다음 사항을 고려하세요:
- 구체적이고 실용적인 조언 제공
- 한국의 경제 상황과 세금 제도를 반영
- 사용자의 연령대와 소득 수준에 맞는 맞춤형 조언
- 단계별 실행 가능한 액션 플랜 제시
- 긍정적이고 격려하는 톤 유지

항상 한국어로 답변하고, 금액은 원화로 표시하되 천 단위 구분자를 사용하세요."""
    
    def process_query(self, user_query: str, user_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """예산 관련 질의 처리"""
        try:
            # 사용자 데이터 검증
            if user_data:
                validated_data = validate_user_input(user_data)
            else:
                validated_data = None
            
            # 컨텍스트 생성
            context = self._create_context(validated_data)
            
            # 메시지 생성
            messages = self._create_messages(user_query, context)
            
            # 응답 생성
            response = self._get_response(messages)
            
            # 메모리 업데이트
            self.update_memory(user_query, response)
            
            return self._format_response(response, "budget")
            
        except Exception as e:
            self.logger.error(f"예산 분석 중 오류: {e}")
            error_response = f"예산 분석 중 오류가 발생했습니다: {str(e)}"
            return self._format_response(error_response, "budget")
    
    def _create_context(self, user_data: Dict[str, Any] = None) -> str:
        """사용자 데이터 기반 컨텍스트 생성"""
        if not user_data:
            return "사용자 데이터가 제공되지 않았습니다. 일반적인 예산 관리 조언을 제공합니다."
        
        try:
            # 기본 재무 지표 계산
            metrics = calculate_basic_metrics(
                user_data.get('income', 0),
                user_data.get('expenses', 0),
                user_data.get('savings', 0)
            )
            
            context = f"""
사용자 재무 현황:
- 나이: {user_data.get('age', 'N/A')}세
- 연소득: {format_currency(user_data.get('income', 0))}
- 연지출: {format_currency(user_data.get('expenses', 0))}
- 저축금: {format_currency(user_data.get('savings', 0))}

재무 지표:
- 순소득: {format_currency(metrics['net_income'])}
- 저축률: {metrics['savings_rate']:.1f}%
- 비상금 보유 개월: {metrics['emergency_fund_months']:.1f}개월
- 재무 건강도 점수: {metrics['financial_health_score']:.0f}/100
"""
            
            # 월별 지출 내역이 있으면 추가
            if 'monthly_expenses' in user_data:
                context += "\n월별 지출 내역:\n"
                for category, amount in user_data['monthly_expenses'].items():
                    context += f"- {category}: {format_currency(amount)}\n"
            
            return context
            
        except Exception as e:
            self.logger.error(f"컨텍스트 생성 중 오류: {e}")
            return "사용자 데이터 처리 중 오류가 발생했습니다."
    
    def analyze_spending_patterns(self, monthly_expenses: Dict[str, float]) -> Dict[str, Any]:
        """지출 패턴 분석"""
        total_expenses = sum(monthly_expenses.values())
        analysis = {
            "total_monthly": total_expenses,
            "total_yearly": total_expenses * 12,
            "categories": {}
        }
        
        for category, amount in monthly_expenses.items():
            percentage = (amount / total_expenses) * 100 if total_expenses > 0 else 0
            analysis["categories"][category] = {
                "amount": amount,
                "percentage": percentage,
                "recommendation": self._get_category_recommendation(category, percentage)
            }
        
        return analysis
    
    def _get_category_recommendation(self, category: str, percentage: float) -> str:
        """카테고리별 지출 권장사항"""
        recommendations = {
            "housing": {
                "high": "주거비가 높습니다. 전세/월세 조건 재검토나 더 저렴한 지역 고려를 권장합니다.",
                "normal": "주거비가 적절한 수준입니다.",
                "low": "주거비가 낮아 여유가 있습니다."
            },
            "food": {
                "high": "식비가 높습니다. 외식 빈도 줄이기나 식재료 구매 최적화를 권장합니다.",
                "normal": "식비가 적절한 수준입니다.",
                "low": "식비가 낮아 여유가 있습니다."
            },
            "transportation": {
                "high": "교통비가 높습니다. 대중교통 이용이나 카풀을 고려해보세요.",
                "normal": "교통비가 적절한 수준입니다.",
                "low": "교통비가 낮아 여유가 있습니다."
            }
        }
        
        if category in recommendations:
            if percentage > 40:
                return recommendations[category]["high"]
            elif percentage > 20:
                return recommendations[category]["normal"]
            else:
                return recommendations[category]["low"]
        
        return "해당 카테고리의 지출을 모니터링하세요."
    
    def create_budget_plan(self, income: float, goals: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        """예산 계획 수립"""
        # 50/30/20 법칙 적용
        needs = income * 0.5  # 필수 지출
        wants = income * 0.3  # 선택적 지출
        savings = income * 0.2  # 저축/투자
        
        budget_plan = {
            "monthly_income": income,
            "budget_allocation": {
                "필수지출(50%)": needs,
                "선택지출(30%)": wants,
                "저축투자(20%)": savings
            },
            "recommendations": [
                "필수지출은 주거비, 식비, 교통비, 보험료 등 생계에 필요한 지출입니다.",
                "선택지출은 여가, 엔터테인먼트, 쇼핑 등 선택적 지출입니다.",
                "저축투자는 비상금, 투자, 목표 자금 마련에 사용하세요."
            ]
        }
        
        # 목표가 있으면 추가 조언
        if goals:
            budget_plan["goal_based_recommendations"] = self._analyze_goals(goals, savings)
        
        return budget_plan
    
    def _analyze_goals(self, goals: List[Dict[str, Any]], monthly_savings: float) -> List[str]:
        """목표 기반 조언 생성"""
        recommendations = []
        
        for goal in goals:
            target_amount = goal.get('target_amount', 0)
            target_year = goal.get('target_year', 1)
            goal_name = goal.get('goal', '목표')
            
            required_monthly = target_amount / (target_year * 12)
            
            if required_monthly > monthly_savings:
                recommendations.append(
                    f"{goal_name} 목표 달성을 위해서는 월 {format_currency(required_monthly)}가 필요합니다. "
                    f"현재 저축 가능 금액({format_currency(monthly_savings)})보다 {format_currency(required_monthly - monthly_savings)} 더 필요합니다. "
                    "목표 기간을 늘리거나 목표 금액을 조정하는 것을 고려해보세요."
                )
            else:
                recommendations.append(
                    f"{goal_name} 목표 달성이 가능합니다. 월 {format_currency(required_monthly)}를 저축하면 목표를 달성할 수 있습니다."
                )
        
        return recommendations
