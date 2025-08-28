"""
세금 관리 전문 에이전트
세금 절약 전략, 연말정산 최적화, 세무 상담 등을 담당하는 AI 에이전트
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

class TaxDeductionAnalysisTool(BaseTool):
    """세금공제 분석 도구"""
    
    name: str = "tax_deduction_analysis"
    description: str = "연말정산에서 활용할 수 있는 세금공제 항목을 분석합니다."
    
    def _run(self, user_data: str) -> str:
        """세금공제 분석 실행"""
        try:
            data = json.loads(user_data)
            
            income = data.get('income', 0)
            age = data.get('age', 30)
            has_children = data.get('has_children', False)
            has_medical_expenses = data.get('has_medical_expenses', False)
            has_education_expenses = data.get('has_education_expenses', False)
            has_insurance = data.get('has_insurance', False)
            has_credit_card = data.get('has_credit_card', False)
            
            # 기본공제
            basic_deduction = 1500000  # 기본공제 150만원
            
            # 추가공제 계산
            additional_deductions = {}
            
            # 연령별 추가공제
            if age >= 65:
                additional_deductions["노인공제"] = 1000000
            elif age >= 55:
                additional_deductions["노인공제"] = 500000
            
            # 자녀공제
            if has_children:
                additional_deductions["자녀공제"] = 1500000
            
            # 의료비공제
            if has_medical_expenses:
                additional_deductions["의료비공제"] = 1200000
            
            # 교육비공제
            if has_education_expenses:
                additional_deductions["교육비공제"] = 3000000
            
            # 보험료공제
            if has_insurance:
                additional_deductions["보험료공제"] = 1200000
            
            # 신용카드공제
            if has_credit_card:
                additional_deductions["신용카드공제"] = 300000
            
            # 총 공제액 계산
            total_deduction = basic_deduction + sum(additional_deductions.values())
            
            # 세금 절약액 계산 (대략적)
            tax_savings = total_deduction * 0.15  # 15% 세율 가정
            
            analysis = {
                "basic_deduction": basic_deduction,
                "additional_deductions": additional_deductions,
                "total_deduction": total_deduction,
                "estimated_tax_savings": tax_savings,
                "recommendations": self._generate_deduction_recommendations(data)
            }
            
            return json.dumps(analysis, ensure_ascii=False, indent=2)
            
        except Exception as e:
            logger.error(f"세금공제 분석 실패: {e}")
            return json.dumps({"error": str(e)})
    
    def _generate_deduction_recommendations(self, data: Dict[str, Any]) -> List[str]:
        """공제 추천사항 생성"""
        recommendations = []
        
        if not data.get('has_credit_card', False):
            recommendations.append("신용카드 사용을 늘려서 소득공제를 받으세요.")
        
        if not data.get('has_insurance', False):
            recommendations.append("보험 가입을 통해 보험료공제를 활용하세요.")
        
        if not data.get('has_medical_expenses', False):
            recommendations.append("의료비 영수증을 보관하여 의료비공제를 받으세요.")
        
        if not data.get('has_education_expenses', False):
            recommendations.append("교육비 지출 시 영수증을 보관하여 교육비공제를 받으세요.")
        
        return recommendations

class InvestmentTaxAnalysisTool(BaseTool):
    """투자 관련 세금 분석 도구"""
    
    name: str = "investment_tax_analysis"
    description: str = "투자 관련 세금을 분석하고 절세 전략을 제시합니다."
    
    def _run(self, investment_data: str) -> str:
        """투자 세금 분석 실행"""
        try:
            data = json.loads(investment_data)
            
            investment_type = data.get('investment_type', 'stocks')
            holding_period = data.get('holding_period', 1)  # 보유 기간 (년)
            profit_amount = data.get('profit_amount', 0)
            loss_amount = data.get('loss_amount', 0)
            
            # 양도소득세 계산
            tax_info = self._calculate_capital_gains_tax(
                investment_type, holding_period, profit_amount, loss_amount
            )
            
            # 절세 전략
            tax_strategies = self._generate_tax_strategies(data)
            
            analysis = {
                "tax_info": tax_info,
                "tax_strategies": tax_strategies,
                "recommendations": self._generate_investment_tax_recommendations(data)
            }
            
            return json.dumps(analysis, ensure_ascii=False, indent=2)
            
        except Exception as e:
            logger.error(f"투자 세금 분석 실패: {e}")
            return json.dumps({"error": str(e)})
    
    def _calculate_capital_gains_tax(self, investment_type: str, holding_period: float, 
                                   profit_amount: float, loss_amount: float) -> Dict[str, Any]:
        """양도소득세 계산"""
        net_profit = profit_amount - loss_amount
        
        if net_profit <= 0:
            return {
                "taxable_amount": 0,
                "tax_rate": 0,
                "tax_amount": 0,
                "note": "손실이 발생하여 세금이 없습니다."
            }
        
        # 보유기간별 세율
        if holding_period >= 3:
            tax_rate = 0.06  # 장기 보유 (3년 이상)
        elif holding_period >= 1:
            tax_rate = 0.15  # 중기 보유 (1-3년)
        else:
            tax_rate = 0.25  # 단기 보유 (1년 미만)
        
        tax_amount = net_profit * tax_rate
        
        return {
            "taxable_amount": net_profit,
            "tax_rate": tax_rate * 100,
            "tax_amount": tax_amount,
            "note": f"{holding_period}년 보유 시 {tax_rate*100}% 세율 적용"
        }
    
    def _generate_tax_strategies(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """절세 전략 생성"""
        strategies = []
        
        # 장기 보유 전략
        strategies.append({
            "strategy": "장기 보유",
            "description": "3년 이상 보유하여 6% 세율 적용",
            "benefit": "세율 절감 효과"
        })
        
        # 손실 상계 전략
        if data.get('loss_amount', 0) > 0:
            strategies.append({
                "strategy": "손실 상계",
                "description": "투자 손실을 이익과 상계하여 과세표준 감소",
                "benefit": "세금 절약"
            })
        
        # ISA 활용
        strategies.append({
            "strategy": "ISA 활용",
            "description": "개인종합자산계좌를 통한 세금 혜택",
            "benefit": "양도소득세 면제"
        })
        
        return strategies
    
    def _generate_investment_tax_recommendations(self, data: Dict[str, Any]) -> List[str]:
        """투자 세금 추천사항"""
        recommendations = []
        
        holding_period = data.get('holding_period', 1)
        
        if holding_period < 3:
            recommendations.append("장기 보유를 통해 세율을 낮추세요.")
        
        recommendations.append("ISA 계좌를 활용하여 세금 혜택을 받으세요.")
        recommendations.append("투자 손실이 있다면 이익과 상계하여 세금을 절약하세요.")
        recommendations.append("연금저축, IRP 등을 활용하여 세금 공제를 받으세요.")
        
        return recommendations

class BusinessTaxAnalysisTool(BaseTool):
    """사업자 세금 분석 도구"""
    
    name: str = "business_tax_analysis"
    description: str = "사업자의 세금을 분석하고 절세 전략을 제시합니다."
    
    def _run(self, business_data: str) -> str:
        """사업자 세금 분석 실행"""
        try:
            data = json.loads(business_data)
            
            revenue = data.get('revenue', 0)
            expenses = data.get('expenses', 0)
            business_type = data.get('business_type', 'individual')
            
            # 소득금액 계산
            income = revenue - expenses
            
            # 세율 계산
            tax_info = self._calculate_business_tax(income, business_type)
            
            # 필요경비 최적화
            expense_optimization = self._optimize_expenses(data)
            
            analysis = {
                "income": income,
                "tax_info": tax_info,
                "expense_optimization": expense_optimization,
                "recommendations": self._generate_business_tax_recommendations(data)
            }
            
            return json.dumps(analysis, ensure_ascii=False, indent=2)
            
        except Exception as e:
            logger.error(f"사업자 세금 분석 실패: {e}")
            return json.dumps({"error": str(e)})
    
    def _calculate_business_tax(self, income: float, business_type: str) -> Dict[str, Any]:
        """사업자 세금 계산"""
        if income <= 0:
            return {
                "taxable_income": 0,
                "tax_rate": 0,
                "tax_amount": 0,
                "note": "소득이 없어 세금이 없습니다."
            }
        
        # 소득세 세율 (간이 계산)
        if income <= 12000000:
            tax_rate = 0.06
        elif income <= 46000000:
            tax_rate = 0.15
        elif income <= 88000000:
            tax_rate = 0.24
        elif income <= 150000000:
            tax_rate = 0.35
        elif income <= 300000000:
            tax_rate = 0.38
        elif income <= 500000000:
            tax_rate = 0.40
        else:
            tax_rate = 0.42
        
        tax_amount = income * tax_rate
        
        return {
            "taxable_income": income,
            "tax_rate": tax_rate * 100,
            "tax_amount": tax_amount,
            "note": f"소득세 {tax_rate*100}% 적용"
        }
    
    def _optimize_expenses(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """필요경비 최적화"""
        optimizations = []
        
        # 사업용 경비
        optimizations.append({
            "category": "사업용 경비",
            "items": ["사무실 임대료", "사업용 차량", "사업용 전화비"],
            "description": "사업과 직접 관련된 경비는 필요경비로 인정"
        })
        
        # 감가상각
        optimizations.append({
            "category": "감가상각",
            "items": ["사업용 장비", "사업용 차량", "사업용 건물"],
            "description": "자산의 감가상각비를 필요경비로 처리"
        })
        
        # 부가가치세
        optimizations.append({
            "category": "부가가치세",
            "items": ["매입세액공제", "세금계산서 발행"],
            "description": "매입세액공제를 통한 부가가치세 절약"
        })
        
        return optimizations
    
    def _generate_business_tax_recommendations(self, data: Dict[str, Any]) -> List[str]:
        """사업자 세금 추천사항"""
        recommendations = []
        
        recommendations.append("모든 사업 관련 경비의 영수증을 보관하세요.")
        recommendations.append("사업용 계좌와 개인 계좌를 분리하여 관리하세요.")
        recommendations.append("세금계산서를 정확히 발행하여 부가가치세를 절약하세요.")
        recommendations.append("감가상각을 활용하여 필요경비를 늘리세요.")
        recommendations.append("연말정산 시 모든 공제 항목을 확인하세요.")
        
        return recommendations

class TaxAgent(BaseAgent):
    """세금 관리 전문 에이전트"""
    
    def __init__(self):
        """세금 관리 에이전트 초기화"""
        super().__init__(
            agent_name="세금 관리 어드바이저",
            agent_role="세금 절약 전략, 연말정산 최적화, 세무 상담을 담당하는 전문가"
        )
        
        # 전문 도구 추가
        self.add_tool(TaxDeductionAnalysisTool())
        self.add_tool(InvestmentTaxAnalysisTool())
        self.add_tool(BusinessTaxAnalysisTool())
        
        # 에이전트 실행기 초기화
        self.initialize_agent_executor()
    
    def _extend_system_prompt(self, base_prompt: str) -> str:
        """세금 관리 전문 프롬프트 확장"""
        specialized_prompt = """
세금 관리 전문가로서 다음 영역에 특화되어 있습니다:

1. 연말정산 최적화
- 세금공제 항목 분석 및 활용
- 기본공제 및 추가공제 최적화
- 신용카드 사용 내역 정리
- 의료비, 교육비, 보험료 공제

2. 투자 관련 세금
- 양도소득세 계산 및 절세 전략
- 장기 보유를 통한 세율 절감
- 손실 상계 전략
- ISA, 연금저축 등 세금 혜택 상품

3. 사업자 세금
- 필요경비 최적화
- 부가가치세 관리
- 감가상각 활용
- 세무 신고 최적화

4. 세금 절약 전략
- 합법적인 절세 방법 제시
- 세금 혜택 상품 활용
- 정기적인 세무 점검
- 세무사 상담 시기 조언

5. 세무 준비
- 세무 신고 준비사항
- 필요 서류 및 영수증 관리
- 세무 신고 일정 관리
- 세무 관련 법규 변경사항

답변 시 다음을 포함하세요:
- 구체적인 세금 계산 과정
- 절세 효과의 정량적 분석
- 단계별 실행 계획
- 주의사항 및 리스크
- 전문가 상담 필요성 언급

주의사항:
- 합법적인 절세 방법만 제시
- 세무 관련 법규 준수 강조
- 복잡한 세무 문제는 전문가 상담 권장
- 개인 상황에 따른 맞춤형 조언 제공
"""
        
        return base_prompt + specialized_prompt
    
    def analyze_tax_deductions(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """세금공제 분석 수행"""
        try:
            deduction_result = self.tools[0]._run(json.dumps(user_data))
            return json.loads(deduction_result)
            
        except Exception as e:
            logger.error(f"세금공제 분석 실패: {e}")
            return {"error": str(e)}
    
    def analyze_investment_tax(self, investment_data: Dict[str, Any]) -> Dict[str, Any]:
        """투자 세금 분석 수행"""
        try:
            tax_result = self.tools[1]._run(json.dumps(investment_data))
            return json.loads(tax_result)
            
        except Exception as e:
            logger.error(f"투자 세금 분석 실패: {e}")
            return {"error": str(e)}
    
    def analyze_business_tax(self, business_data: Dict[str, Any]) -> Dict[str, Any]:
        """사업자 세금 분석 수행"""
        try:
            business_result = self.tools[2]._run(json.dumps(business_data))
            return json.loads(business_result)
            
        except Exception as e:
            logger.error(f"사업자 세금 분석 실패: {e}")
            return {"error": str(e)}
    
    def get_tax_savings_strategies(self, user_data: Dict[str, Any]) -> List[str]:
        """세금 절약 전략 생성"""
        strategies = []
        
        # 세금공제 분석
        deduction_analysis = self.analyze_tax_deductions(user_data)
        if 'recommendations' in deduction_analysis:
            strategies.extend(deduction_analysis['recommendations'])
        
        # 투자 세금 분석
        if 'investment_type' in user_data:
            investment_tax = self.analyze_investment_tax(user_data)
            if 'recommendations' in investment_tax:
                strategies.extend(investment_tax['recommendations'])
        
        # 사업자 세금 분석
        if user_data.get('is_business_owner', False):
            business_tax = self.analyze_business_tax(user_data)
            if 'recommendations' in business_tax:
                strategies.extend(business_tax['recommendations'])
        
        return list(set(strategies))  # 중복 제거
    
    def get_specialized_tools(self) -> List[BaseTool]:
        """전문 도구 목록 반환"""
        return [
            TaxDeductionAnalysisTool(),
            InvestmentTaxAnalysisTool(),
            BusinessTaxAnalysisTool()
        ]
    
    def get_specialized_prompt(self) -> str:
        """전문 프롬프트 반환"""
        return """
당신은 세금 관리 전문가입니다. 다음 영역에서 전문성을 발휘하세요:

1. 연말정산 최적화 및 세금공제
2. 투자 관련 세금 절세 전략
3. 사업자 세금 관리
4. 세금 혜택 상품 활용
5. 합법적인 절세 방법 제시

항상 법규를 준수하는 합법적인 조언을 제공하세요.
"""
