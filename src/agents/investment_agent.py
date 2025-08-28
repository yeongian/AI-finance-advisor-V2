"""
투자 관리 전문 에이전트
포트폴리오 분석, 투자 전략 수립, 위험 관리 등을 담당하는 AI 에이전트
"""

import logging
from typing import Dict, Any, List, Optional
import json
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta

from langchain.tools import BaseTool, tool
from langchain.schema import Document

from .base_agent import BaseAgent
from ..core.utils import format_currency, format_percentage, calculate_returns, get_stock_data
from ..rag.knowledge_base import KnowledgeBase

logger = logging.getLogger(__name__)

class PortfolioAnalysisTool(BaseTool):
    """포트폴리오 분석 도구"""
    
    name: str = "portfolio_analysis"
    description: str = "현재 투자 포트폴리오를 분석하여 성과와 위험도를 평가합니다."
    
    def _run(self, portfolio_data: str) -> str:
        """포트폴리오 분석 실행"""
        try:
            data = json.loads(portfolio_data)
            current_investments = data.get('current_investments', {})
            
            total_value = sum(current_investments.values())
            
            if total_value == 0:
                return json.dumps({
                    "total_value": 0,
                    "allocation": {},
                    "risk_score": 0,
                    "recommendations": ["투자 포트폴리오가 없습니다. 투자 계획을 수립해보세요."]
                })
            
            # 자산 배분 분석
            allocation = {}
            for asset_type, amount in current_investments.items():
                allocation[asset_type] = {
                    "amount": amount,
                    "percentage": (amount / total_value) * 100
                }
            
            # 위험도 점수 계산
            risk_weights = {
                "stocks": 0.8,
                "bonds": 0.3,
                "real_estate": 0.6,
                "crypto": 0.9,
                "cash": 0.1
            }
            
            risk_score = sum(
                allocation[asset]["percentage"] * risk_weights.get(asset, 0.5) / 100
                for asset in allocation
            )
            
            # 추천사항 생성
            recommendations = self._generate_portfolio_recommendations(allocation, risk_score)
            
            analysis = {
                "total_value": total_value,
                "allocation": allocation,
                "risk_score": risk_score,
                "recommendations": recommendations
            }
            
            return json.dumps(analysis, ensure_ascii=False, indent=2)
            
        except Exception as e:
            logger.error(f"포트폴리오 분석 실패: {e}")
            return json.dumps({"error": str(e)})
    
    def _generate_portfolio_recommendations(self, allocation: Dict, risk_score: float) -> List[str]:
        """포트폴리오 추천사항 생성"""
        recommendations = []
        
        # 위험도 기반 추천
        if risk_score > 0.7:
            recommendations.append("포트폴리오 위험도가 높습니다. 안전자산 비중을 늘리세요.")
        elif risk_score < 0.3:
            recommendations.append("포트폴리오가 너무 보수적입니다. 성장자산 비중을 늘려보세요.")
        
        # 자산 배분 기반 추천
        stocks_pct = allocation.get("stocks", {}).get("percentage", 0)
        bonds_pct = allocation.get("bonds", {}).get("percentage", 0)
        cash_pct = allocation.get("cash", {}).get("percentage", 0)
        
        if stocks_pct > 80:
            recommendations.append("주식 비중이 너무 높습니다. 분산 투자를 고려하세요.")
        
        if bonds_pct < 10:
            recommendations.append("채권 비중이 낮습니다. 안정성을 위해 채권 비중을 늘리세요.")
        
        if cash_pct > 30:
            recommendations.append("현금 비중이 높습니다. 투자 기회를 놓치지 마세요.")
        
        return recommendations

class InvestmentRecommendationTool(BaseTool):
    """투자 추천 도구"""
    
    name: str = "investment_recommendation"
    description: str = "사용자의 상황에 맞는 투자 상품을 추천합니다."
    
    def _run(self, user_profile: str) -> str:
        """투자 추천 실행"""
        try:
            data = json.loads(user_profile)
            
            age = data.get('age', 30)
            risk_tolerance = data.get('risk_tolerance', 'moderate')
            investment_amount = data.get('investment_amount', 0)
            investment_horizon = data.get('investment_horizon', 10)
            
            # 나이 기반 자산 배분
            stock_ratio = max(20, 100 - age)
            bond_ratio = min(80, age)
            cash_ratio = 10
            
            # 위험 성향 조정
            if risk_tolerance == 'conservative':
                stock_ratio *= 0.7
                bond_ratio *= 1.3
            elif risk_tolerance == 'aggressive':
                stock_ratio *= 1.3
                bond_ratio *= 0.7
            
            # 정규화
            total = stock_ratio + bond_ratio + cash_ratio
            stock_ratio = stock_ratio / total * 100
            bond_ratio = bond_ratio / total * 100
            cash_ratio = cash_ratio / total * 100
            
            # 추천 상품
            recommendations = self._get_product_recommendations(
                stock_ratio, bond_ratio, cash_ratio, investment_amount
            )
            
            result = {
                "asset_allocation": {
                    "stocks": stock_ratio,
                    "bonds": bond_ratio,
                    "cash": cash_ratio
                },
                "recommendations": recommendations,
                "risk_level": self._get_risk_level(stock_ratio)
            }
            
            return json.dumps(result, ensure_ascii=False, indent=2)
            
        except Exception as e:
            logger.error(f"투자 추천 실패: {e}")
            return json.dumps({"error": str(e)})
    
    def _get_product_recommendations(self, stock_ratio: float, bond_ratio: float, 
                                   cash_ratio: float, amount: float) -> List[Dict]:
        """상품 추천"""
        recommendations = []
        
        if stock_ratio > 0:
            stock_amount = amount * stock_ratio / 100
            recommendations.append({
                "category": "주식형",
                "products": [
                    "KODEX 200 ETF (069500)",
                    "TIGER 코스피200 ETF (102110)",
                    "미국 S&P 500 ETF (SPY)"
                ],
                "amount": stock_amount,
                "description": "장기 성장을 위한 주식형 상품"
            })
        
        if bond_ratio > 0:
            bond_amount = amount * bond_ratio / 100
            recommendations.append({
                "category": "채권형",
                "products": [
                    "국채 ETF",
                    "회사채 ETF",
                    "단기채권 펀드"
                ],
                "amount": bond_amount,
                "description": "안정성과 수익성을 위한 채권형 상품"
            })
        
        if cash_ratio > 0:
            cash_amount = amount * cash_ratio / 100
            recommendations.append({
                "category": "현금성",
                "products": [
                    "MMF (머니마켓펀드)",
                    "단기 예금",
                    "국채 단기 펀드"
                ],
                "amount": cash_amount,
                "description": "유동성과 안정성을 위한 현금성 상품"
            })
        
        return recommendations
    
    def _get_risk_level(self, stock_ratio: float) -> str:
        """위험도 수준 판정"""
        if stock_ratio > 70:
            return "높음"
        elif stock_ratio > 40:
            return "보통"
        else:
            return "낮음"

class MarketAnalysisTool(BaseTool):
    """시장 분석 도구"""
    
    name: str = "market_analysis"
    description: str = "주식 시장 동향을 분석하고 투자 기회를 찾습니다."
    
    def _run(self, analysis_request: str) -> str:
        """시장 분석 실행"""
        try:
            data = json.loads(analysis_request)
            symbols = data.get('symbols', ['^KS11', '^GSPC'])  # KOSPI, S&P 500
            
            market_data = {}
            
            for symbol in symbols:
                try:
                    stock_data = get_stock_data(symbol, period="1y")
                    if not stock_data.empty:
                        returns = calculate_returns(stock_data['Close'])
                        market_data[symbol] = {
                            "current_price": stock_data['Close'].iloc[-1],
                            "total_return": returns["total_return"],
                            "annualized_return": returns["annualized_return"],
                            "volatility": stock_data['Close'].pct_change().std() * 100
                        }
                except Exception as e:
                    logger.warning(f"데이터 가져오기 실패: {symbol}, {e}")
            
            # 시장 동향 분석
            analysis = {
                "market_data": market_data,
                "trend_analysis": self._analyze_trends(market_data),
                "recommendations": self._generate_market_recommendations(market_data)
            }
            
            return json.dumps(analysis, ensure_ascii=False, indent=2)
            
        except Exception as e:
            logger.error(f"시장 분석 실패: {e}")
            return json.dumps({"error": str(e)})
    
    def _analyze_trends(self, market_data: Dict) -> Dict:
        """시장 동향 분석"""
        trends = {}
        
        for symbol, data in market_data.items():
            if data["total_return"] > 10:
                trends[symbol] = "상승세"
            elif data["total_return"] < -10:
                trends[symbol] = "하락세"
            else:
                trends[symbol] = "횡보세"
        
        return trends
    
    def _generate_market_recommendations(self, market_data: Dict) -> List[str]:
        """시장 기반 추천사항"""
        recommendations = []
        
        # KOSPI 분석
        kospi_data = market_data.get('^KS11', {})
        if kospi_data:
            if kospi_data["total_return"] > 20:
                recommendations.append("KOSPI가 강세입니다. 단, 과열 가능성을 고려하세요.")
            elif kospi_data["total_return"] < -10:
                recommendations.append("KOSPI가 약세입니다. 저평가 기회를 모니터링하세요.")
        
        # S&P 500 분석
        sp500_data = market_data.get('^GSPC', {})
        if sp500_data:
            if sp500_data["total_return"] > 15:
                recommendations.append("미국 시장이 강세입니다. 글로벌 분산 투자를 고려하세요.")
        
        return recommendations

class InvestmentAgent(BaseAgent):
    """투자 관리 전문 에이전트"""
    
    def __init__(self):
        """투자 관리 에이전트 초기화"""
        super().__init__(
            agent_name="투자 관리 어드바이저",
            agent_role="포트폴리오 분석, 투자 전략 수립, 위험 관리를 담당하는 전문가"
        )
        
        # 전문 도구 추가
        self.add_tool(PortfolioAnalysisTool())
        self.add_tool(InvestmentRecommendationTool())
        self.add_tool(MarketAnalysisTool())
        
        # 에이전트 실행기 초기화
        self.initialize_agent_executor()
    
    def _extend_system_prompt(self, base_prompt: str) -> str:
        """투자 관리 전문 프롬프트 확장"""
        specialized_prompt = """
투자 관리 전문가로서 다음 영역에 특화되어 있습니다:

1. 포트폴리오 분석
- 현재 투자 포트폴리오 성과 평가
- 자산 배분 최적화
- 위험도 분석 및 관리
- 수익률 및 변동성 분석

2. 투자 전략 수립
- 개인 상황에 맞는 투자 전략 제시
- 자산 배분 전략 (100-나이 법칙 등)
- 분산 투자 전략
- 정기 리밸런싱 계획

3. 투자 상품 추천
- ETF, 펀드, 주식 등 상품 추천
- 위험도별 상품 매칭
- 수수료 및 성과 비교
- 투자 시점 조언

4. 시장 분석
- 국내외 시장 동향 분석
- 경제 지표 해석
- 투자 기회 포착
- 리스크 관리

5. 위험 관리
- 투자 한도 설정
- 손실 제한 전략
- 비상금 관리
- 보험 및 연금 연계

답변 시 다음을 포함하세요:
- 구체적인 수치와 계산 과정
- 위험도 평가 및 관리 방안
- 단계별 투자 실행 계획
- 정기적인 포트폴리오 점검 방법
- 투자 관련 세금 고려사항

주의사항:
- 투자에는 항상 위험이 따름을 명시
- 과거 성과가 미래 수익을 보장하지 않음을 강조
- 개인 투자 판단의 중요성 강조
- 전문 투자 상담의 필요성 언급
"""
        
        return base_prompt + specialized_prompt
    
    def analyze_portfolio(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """포트폴리오 분석 수행"""
        try:
            portfolio_result = self.tools[0]._run(json.dumps(user_data))
            return json.loads(portfolio_result)
            
        except Exception as e:
            logger.error(f"포트폴리오 분석 실패: {e}")
            return {"error": str(e)}
    
    def get_investment_recommendations(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """투자 추천 수행"""
        try:
            recommendation_result = self.tools[1]._run(json.dumps(user_data))
            return json.loads(recommendation_result)
            
        except Exception as e:
            logger.error(f"투자 추천 실패: {e}")
            return {"error": str(e)}
    
    def analyze_market(self, symbols: List[str] = None) -> Dict[str, Any]:
        """시장 분석 수행"""
        try:
            if symbols is None:
                symbols = ['^KS11', '^GSPC']  # KOSPI, S&P 500
            
            market_result = self.tools[2]._run(json.dumps({"symbols": symbols}))
            return json.loads(market_result)
            
        except Exception as e:
            logger.error(f"시장 분석 실패: {e}")
            return {"error": str(e)}
    
    def get_specialized_tools(self) -> List[BaseTool]:
        """전문 도구 목록 반환"""
        return [
            PortfolioAnalysisTool(),
            InvestmentRecommendationTool(),
            MarketAnalysisTool()
        ]
    
    def get_specialized_prompt(self) -> str:
        """전문 프롬프트 반환"""
        return """
당신은 투자 관리 전문가입니다. 다음 영역에서 전문성을 발휘하세요:

1. 포트폴리오 분석 및 최적화
2. 투자 전략 수립
3. 투자 상품 추천
4. 시장 분석 및 동향 파악
5. 위험 관리 및 손실 제한

항상 위험을 고려한 균형잡힌 조언을 제공하세요.
"""
