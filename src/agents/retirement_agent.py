"""
은퇴 계획 전문 에이전트
은퇴 자금 설계, 연금 상품 분석, 은퇴 준비 로드맵 등을 담당하는 AI 에이전트
"""

import logging
from typing import Dict, Any, List, Optional
import json
from datetime import datetime, timedelta

from langchain.tools import BaseTool, tool
from langchain.schema import Document

from .base_agent import BaseAgent
from ..core.utils import format_currency, format_percentage
from ..rag.knowledge_base import KnowledgeBase

logger = logging.getLogger(__name__)

class RetirementGoalCalculatorTool(BaseTool):
    """은퇴 목표 계산 도구"""
    
    name: str = "retirement_goal_calculator"
    description: str = "은퇴 목표 금액을 계산하고 달성 계획을 수립합니다."
    
    def _run(self, user_data: str) -> str:
        """은퇴 목표 계산 실행"""
        try:
            data = json.loads(user_data)
            
            current_age = data.get('current_age', 30)
            retirement_age = data.get('retirement_age', 65)
            current_income = data.get('current_income', 50000000)
            current_savings = data.get('current_savings', 0)
            expected_return = data.get('expected_return', 0.05)  # 5%
            inflation_rate = data.get('inflation_rate', 0.02)  # 2%
            
            # 은퇴까지 남은 기간
            years_to_retirement = retirement_age - current_age
            
            # 은퇴 후 필요 생활비 (현재 생활비의 70%)
            current_living_expenses = current_income * 0.7
            retirement_living_expenses = current_living_expenses * (1 + inflation_rate) ** years_to_retirement
            
            # 은퇴 후 생존 기간 (90세까지 가정)
            years_in_retirement = 90 - retirement_age
            
            # 은퇴 목표 금액 계산
            total_retirement_needs = retirement_living_expenses * years_in_retirement
            
            # 현재 저축액의 미래 가치
            future_savings = current_savings * (1 + expected_return) ** years_to_retirement
            
            # 추가로 필요한 저축액
            additional_savings_needed = total_retirement_needs - future_savings
            
            # 월 저축액 계산
            monthly_savings_needed = additional_savings_needed / (years_to_retirement * 12)
            
            # 연금 수령액 고려
            pension_income = self._calculate_pension_income(data)
            pension_adjustment = pension_income * years_in_retirement
            
            # 최종 필요 저축액
            final_savings_needed = max(0, additional_savings_needed - pension_adjustment)
            final_monthly_savings = final_savings_needed / (years_to_retirement * 12)
            
            analysis = {
                "years_to_retirement": years_to_retirement,
                "retirement_living_expenses": retirement_living_expenses,
                "total_retirement_needs": total_retirement_needs,
                "future_savings": future_savings,
                "additional_savings_needed": additional_savings_needed,
                "monthly_savings_needed": monthly_savings_needed,
                "pension_income": pension_income,
                "final_monthly_savings": final_monthly_savings,
                "feasibility": self._assess_feasibility(final_monthly_savings, current_income),
                "recommendations": self._generate_retirement_recommendations(data, final_monthly_savings)
            }
            
            return json.dumps(analysis, ensure_ascii=False, indent=2)
            
        except Exception as e:
            logger.error(f"은퇴 목표 계산 실패: {e}")
            return json.dumps({"error": str(e)})
    
    def _calculate_pension_income(self, data: Dict[str, Any]) -> float:
        """연금 수령액 계산"""
        current_income = data.get('current_income', 50000000)
        years_worked = data.get('years_worked', 35)
        
        # 국민연금 수령액 (간이 계산)
        # 실제로는 복잡한 계산이 필요하지만, 여기서는 간단히 계산
        pension_rate = 0.4  # 소득대체율 40% 가정
        monthly_pension = (current_income * pension_rate) / 12
        
        return monthly_pension
    
    def _assess_feasibility(self, monthly_savings: float, current_income: float) -> str:
        """달성 가능성 평가"""
        savings_rate = (monthly_savings * 12) / current_income
        
        if savings_rate <= 0.1:
            return "매우 용이"
        elif savings_rate <= 0.2:
            return "용이"
        elif savings_rate <= 0.3:
            return "보통"
        elif savings_rate <= 0.4:
            return "어려움"
        else:
            return "매우 어려움"
    
    def _generate_retirement_recommendations(self, data: Dict[str, Any], monthly_savings: float) -> List[str]:
        """은퇴 추천사항 생성"""
        recommendations = []
        
        if monthly_savings > data.get('current_income', 0) * 0.3 / 12:
            recommendations.append("월 저축액이 높습니다. 은퇴 연령을 늘리거나 생활비를 줄이는 것을 고려하세요.")
        
        if data.get('current_savings', 0) == 0:
            recommendations.append("현재 저축액이 없습니다. 즉시 저축을 시작하세요.")
        
        recommendations.append("연금저축, IRP 등을 활용하여 세금 혜택을 받으세요.")
        recommendations.append("정기적으로 은퇴 계획을 점검하고 조정하세요.")
        
        return recommendations

class PensionProductAnalysisTool(BaseTool):
    """연금 상품 분석 도구"""
    
    name: str = "pension_product_analysis"
    description: str = "다양한 연금 상품을 분석하고 추천합니다."
    
    def _run(self, user_profile: str) -> str:
        """연금 상품 분석 실행"""
        try:
            data = json.loads(user_profile)
            
            age = data.get('age', 30)
            income = data.get('income', 50000000)
            risk_tolerance = data.get('risk_tolerance', 'moderate')
            investment_horizon = data.get('investment_horizon', 30)
            
            # 연금 상품 추천
            recommended_products = self._get_recommended_products(data)
            
            # 상품별 분석
            product_analysis = []
            for product in recommended_products:
                analysis = self._analyze_product(product, data)
                product_analysis.append(analysis)
            
            # 포트폴리오 구성
            portfolio = self._create_pension_portfolio(product_analysis, data)
            
            result = {
                "recommended_products": recommended_products,
                "product_analysis": product_analysis,
                "portfolio": portfolio,
                "recommendations": self._generate_pension_recommendations(data)
            }
            
            return json.dumps(result, ensure_ascii=False, indent=2)
            
        except Exception as e:
            logger.error(f"연금 상품 분석 실패: {e}")
            return json.dumps({"error": str(e)})
    
    def _get_recommended_products(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """추천 연금 상품 목록"""
        products = [
            {
                "name": "국민연금",
                "type": "공적연금",
                "contribution_rate": 0.045,  # 4.5%
                "risk_level": "낮음",
                "tax_benefit": "세금공제",
                "description": "기본적인 공적연금"
            },
            {
                "name": "연금저축",
                "type": "개인연금",
                "contribution_rate": 0.06,  # 6%
                "risk_level": "보통",
                "tax_benefit": "세금공제",
                "description": "세금 혜택이 있는 개인연금"
            },
            {
                "name": "IRP (개인형퇴직연금)",
                "type": "퇴직연금",
                "contribution_rate": 0.13,  # 13%
                "risk_level": "보통",
                "tax_benefit": "세금공제",
                "description": "퇴직금을 연금으로 받는 상품"
            },
            {
                "name": "연금보험",
                "type": "보험형연금",
                "contribution_rate": 0.05,  # 5%
                "risk_level": "낮음",
                "tax_benefit": "세금공제",
                "description": "보험과 연금을 결합한 상품"
            }
        ]
        
        return products
    
    def _analyze_product(self, product: Dict[str, Any], user_data: Dict[str, Any]) -> Dict[str, Any]:
        """개별 상품 분석"""
        income = user_data.get('income', 50000000)
        age = user_data.get('age', 30)
        
        # 연간 납입액 계산
        annual_contribution = income * product["contribution_rate"]
        
        # 세금 절약액 계산
        tax_savings = annual_contribution * 0.15  # 15% 세율 가정
        
        # 적합성 점수 계산
        suitability_score = self._calculate_suitability_score(product, user_data)
        
        return {
            "product": product,
            "annual_contribution": annual_contribution,
            "tax_savings": tax_savings,
            "suitability_score": suitability_score,
            "pros_cons": self._get_pros_cons(product)
        }
    
    def _calculate_suitability_score(self, product: Dict[str, Any], user_data: Dict[str, Any]) -> float:
        """적합성 점수 계산"""
        score = 70  # 기본 점수
        
        # 나이별 조정
        age = user_data.get('age', 30)
        if age < 40 and product["type"] == "공적연금":
            score += 10
        elif age >= 50 and product["type"] == "개인연금":
            score += 15
        
        # 위험 성향 조정
        risk_tolerance = user_data.get('risk_tolerance', 'moderate')
        if risk_tolerance == 'conservative' and product["risk_level"] == "낮음":
            score += 10
        elif risk_tolerance == 'aggressive' and product["risk_level"] != "낮음":
            score += 10
        
        return min(100, score)
    
    def _get_pros_cons(self, product: Dict[str, Any]) -> Dict[str, List[str]]:
        """장단점 분석"""
        pros_cons = {
            "pros": [],
            "cons": []
        }
        
        if product["type"] == "공적연금":
            pros_cons["pros"] = ["안정성", "국가 보장", "자동 관리"]
            pros_cons["cons"] = ["낮은 수익률", "정부 정책 의존"]
        elif product["type"] == "개인연금":
            pros_cons["pros"] = ["세금 혜택", "수익률", "유연성"]
            pros_cons["cons"] = ["수수료", "투자 위험"]
        elif product["type"] == "퇴직연금":
            pros_cons["pros"] = ["높은 한도", "세금 혜택", "이직 시 이전 가능"]
            pros_cons["cons"] = ["복잡성", "관리 비용"]
        
        return pros_cons
    
    def _create_pension_portfolio(self, product_analysis: List[Dict], user_data: Dict[str, Any]) -> Dict[str, Any]:
        """연금 포트폴리오 구성"""
        # 점수 기반 가중치 계산
        total_score = sum(analysis["suitability_score"] for analysis in product_analysis)
        
        portfolio = {}
        for analysis in product_analysis:
            weight = analysis["suitability_score"] / total_score
            portfolio[analysis["product"]["name"]] = {
                "weight": weight,
                "annual_contribution": analysis["annual_contribution"] * weight
            }
        
        return portfolio
    
    def _generate_pension_recommendations(self, data: Dict[str, Any]) -> List[str]:
        """연금 추천사항"""
        recommendations = []
        
        age = data.get('age', 30)
        
        if age < 40:
            recommendations.append("장기 관점에서 다양한 연금 상품에 분산 투자하세요.")
        elif age < 50:
            recommendations.append("연금저축과 IRP를 중심으로 포트폴리오를 구성하세요.")
        else:
            recommendations.append("안정적인 공적연금과 연금보험 비중을 늘리세요.")
        
        recommendations.append("세금 혜택을 최대한 활용하세요.")
        recommendations.append("정기적으로 연금 포트폴리오를 점검하세요.")
        
        return recommendations

class RetirementRoadmapTool(BaseTool):
    """은퇴 로드맵 도구"""
    
    name: str = "retirement_roadmap"
    description: str = "은퇴 준비를 위한 단계별 로드맵을 제공합니다."
    
    def _run(self, user_data: str) -> str:
        """은퇴 로드맵 생성 실행"""
        try:
            data = json.loads(user_data)
            
            current_age = data.get('current_age', 30)
            retirement_age = data.get('retirement_age', 65)
            
            # 단계별 로드맵 생성
            roadmap = self._create_roadmap(current_age, retirement_age)
            
            # 현재 단계 확인
            current_stage = self._identify_current_stage(current_age, roadmap)
            
            # 액션 플랜 생성
            action_plan = self._create_action_plan(current_stage, data)
            
            result = {
                "roadmap": roadmap,
                "current_stage": current_stage,
                "action_plan": action_plan,
                "milestones": self._create_milestones(current_age, retirement_age)
            }
            
            return json.dumps(result, ensure_ascii=False, indent=2)
            
        except Exception as e:
            logger.error(f"은퇴 로드맵 생성 실패: {e}")
            return json.dumps({"error": str(e)})
    
    def _create_roadmap(self, current_age: int, retirement_age: int) -> List[Dict[str, Any]]:
        """은퇴 로드맵 생성"""
        roadmap = [
            {
                "stage": "기초 단계 (20-30대)",
                "age_range": "20-35",
                "focus": "기초 자산 형성",
                "actions": [
                    "비상금 확보 (3-6개월치)",
                    "부채 상환",
                    "기본 저축 습관 형성",
                    "연금저축 시작"
                ],
                "target_savings_rate": 0.1
            },
            {
                "stage": "성장 단계 (30-40대)",
                "age_range": "35-45",
                "focus": "자산 축적 가속화",
                "actions": [
                    "투자 포트폴리오 확대",
                    "연금 상품 다양화",
                    "부동산 투자 고려",
                    "자녀 교육비 준비"
                ],
                "target_savings_rate": 0.15
            },
            {
                "stage": "안정화 단계 (40-50대)",
                "age_range": "45-55",
                "focus": "위험 관리 및 안정화",
                "actions": [
                    "포트폴리오 리밸런싱",
                    "연금 수령 계획 수립",
                    "의료보험 점검",
                    "은퇴 후 일자리 준비"
                ],
                "target_savings_rate": 0.20
            },
            {
                "stage": "준비 단계 (50-60대)",
                "age_range": "55-65",
                "focus": "은퇴 준비 완료",
                "actions": [
                    "은퇴 자금 최종 점검",
                    "연금 수령 방식 결정",
                    "은퇴 후 생활 계획 수립",
                    "상속/증여 계획"
                ],
                "target_savings_rate": 0.25
            }
        ]
        
        return roadmap
    
    def _identify_current_stage(self, current_age: int, roadmap: List[Dict]) -> Dict[str, Any]:
        """현재 단계 확인"""
        for stage in roadmap:
            age_range = stage["age_range"]
            start_age, end_age = map(int, age_range.split("-"))
            
            if start_age <= current_age <= end_age:
                return stage
        
        # 기본값
        return roadmap[0]
    
    def _create_action_plan(self, current_stage: Dict[str, Any], user_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """액션 플랜 생성"""
        actions = []
        
        for action in current_stage["actions"]:
            priority = "높음" if "비상금" in action or "부채" in action else "보통"
            timeline = "즉시" if priority == "높음" else "3개월 내"
            
            actions.append({
                "action": action,
                "priority": priority,
                "timeline": timeline,
                "status": "대기"
            })
        
        return actions
    
    def _create_milestones(self, current_age: int, retirement_age: int) -> List[Dict[str, Any]]:
        """주요 마일스톤 생성"""
        milestones = []
        
        # 5년 단위 마일스톤
        for age in range(current_age, retirement_age + 1, 5):
            if age <= retirement_age:
                milestones.append({
                    "age": age,
                    "year": datetime.now().year + (age - current_age),
                    "target": f"{age}세 은퇴 준비 점검",
                    "description": f"{age}세까지의 은퇴 준비 상황을 종합 점검"
                })
        
        return milestones

class RetirementAgent(BaseAgent):
    """은퇴 계획 전문 에이전트"""
    
    def __init__(self):
        """은퇴 계획 에이전트 초기화"""
        super().__init__(
            agent_name="은퇴 계획 어드바이저",
            agent_role="은퇴 자금 설계, 연금 상품 분석, 은퇴 준비 로드맵을 담당하는 전문가"
        )
        
        # 전문 도구 추가
        self.add_tool(RetirementGoalCalculatorTool())
        self.add_tool(PensionProductAnalysisTool())
        self.add_tool(RetirementRoadmapTool())
        
        # 에이전트 실행기 초기화
        self.initialize_agent_executor()
    
    def _extend_system_prompt(self, base_prompt: str) -> str:
        """은퇴 계획 전문 프롬프트 확장"""
        specialized_prompt = """
은퇴 계획 전문가로서 다음 영역에 특화되어 있습니다:

1. 은퇴 목표 설정
- 은퇴 시점 및 목표 금액 설정
- 은퇴 후 생활비 계산
- 인플레이션 고려한 실질 구매력 유지
- 은퇴 목표 달성 가능성 평가

2. 연금 상품 분석
- 공적연금 (국민연금) 분석
- 개인연금 (연금저축, IRP) 분석
- 연금보험 상품 분석
- 세금 혜택 및 수수료 비교

3. 은퇴 자금 설계
- 단계별 저축 계획 수립
- 투자 수익률 및 위험 관리
- 연금 수령 전략 수립
- 은퇴 자금 지속 가능성 분석

4. 은퇴 준비 로드맵
- 연령별 은퇴 준비 단계
- 단계별 목표 및 액션 플랜
- 주요 마일스톤 설정
- 정기적인 점검 및 조정

5. 은퇴 후 관리
- 연금 수령 방식 선택
- 은퇴 후 수입원 다각화
- 의료보험 및 장기요양보험
- 상속 및 증여 계획

답변 시 다음을 포함하세요:
- 구체적인 금액 계산 및 근거
- 단계별 실행 계획
- 위험 요소 및 대응 방안
- 정기적인 점검 방법
- 전문가 상담 필요성

주의사항:
- 장기 관점에서의 계획 수립
- 인플레이션 및 수명 연장 고려
- 다양한 연금 상품의 분산 투자
- 정기적인 계획 조정의 중요성
"""
        
        return base_prompt + specialized_prompt
    
    def calculate_retirement_goal(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """은퇴 목표 계산 수행"""
        try:
            goal_result = self.tools[0]._run(json.dumps(user_data))
            return json.loads(goal_result)
            
        except Exception as e:
            logger.error(f"은퇴 목표 계산 실패: {e}")
            return {"error": str(e)}
    
    def analyze_pension_products(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """연금 상품 분석 수행"""
        try:
            pension_result = self.tools[1]._run(json.dumps(user_data))
            return json.loads(pension_result)
            
        except Exception as e:
            logger.error(f"연금 상품 분석 실패: {e}")
            return {"error": str(e)}
    
    def create_retirement_roadmap(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """은퇴 로드맵 생성 수행"""
        try:
            roadmap_result = self.tools[2]._run(json.dumps(user_data))
            return json.loads(roadmap_result)
            
        except Exception as e:
            logger.error(f"은퇴 로드맵 생성 실패: {e}")
            return {"error": str(e)}
    
    def get_retirement_recommendations(self, user_data: Dict[str, Any]) -> List[str]:
        """은퇴 계획 추천사항 생성"""
        recommendations = []
        
        # 은퇴 목표 분석
        goal_analysis = self.calculate_retirement_goal(user_data)
        if 'recommendations' in goal_analysis:
            recommendations.extend(goal_analysis['recommendations'])
        
        # 연금 상품 분석
        pension_analysis = self.analyze_pension_products(user_data)
        if 'recommendations' in pension_analysis:
            recommendations.extend(pension_analysis['recommendations'])
        
        # 로드맵 분석
        roadmap_analysis = self.create_retirement_roadmap(user_data)
        if 'action_plan' in roadmap_analysis:
            for action in roadmap_analysis['action_plan']:
                if action['priority'] == '높음':
                    recommendations.append(f"우선순위: {action['action']}")
        
        return list(set(recommendations))  # 중복 제거
    
    def get_specialized_tools(self) -> List[BaseTool]:
        """전문 도구 목록 반환"""
        return [
            RetirementGoalCalculatorTool(),
            PensionProductAnalysisTool(),
            RetirementRoadmapTool()
        ]
    
    def get_specialized_prompt(self) -> str:
        """전문 프롬프트 반환"""
        return """
당신은 은퇴 계획 전문가입니다. 다음 영역에서 전문성을 발휘하세요:

1. 은퇴 목표 설정 및 자금 설계
2. 연금 상품 분석 및 포트폴리오 구성
3. 단계별 은퇴 준비 로드맵
4. 은퇴 후 수입원 다각화
5. 장기 관점의 재무 계획

항상 장기적이고 지속 가능한 은퇴 계획을 제시하세요.
"""
