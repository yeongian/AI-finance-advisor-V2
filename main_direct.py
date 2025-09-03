#!/usr/bin/env python3
"""
AI 개인 재무 관리 어드바이저 - 직접 실행 버전
API 서버 없이 모든 기능을 직접 실행하는 통합 애플리케이션
"""

import streamlit as st
import json
import logging
from datetime import datetime
import time
import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# 페이지 설정
st.set_page_config(
    page_title="AI 재무관리 어드바이저 (직접 실행)",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# plotly import를 안전하게 처리
try:
    import plotly.graph_objects as go
    import plotly.express as px
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False
    st.warning("⚠️ plotly가 설치되지 않았습니다. 차트 기능이 제한됩니다.")

import pandas as pd
import numpy as np

# 환경 변수 로딩
load_dotenv()

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/streamlit_direct.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# 직접 실행을 위한 핵심 모듈들 import (안전한 import)
try:
    from src.core.config import settings
    from src.rag.knowledge_base import KnowledgeBase
    from src.agents.multi_agent_system import MultiAgentSystem
    from src.core.financial_data import financial_data
    from src.core.portfolio_simulator import portfolio_simulator
    from src.core.advanced_ai import advanced_ai
    FULL_FEATURES_AVAILABLE = True
    logger.info("✅ 전체 기능 모듈 로드 성공")
except ImportError as e:
    logger.warning(f"⚠️ 전체 기능 모듈 로드 실패: {e}")
    logger.info("🔄 간단 모드로 전환합니다.")
    FULL_FEATURES_AVAILABLE = False

class DirectFinanceAdvisor:
    """API 서버 없이 직접 실행하는 재무 관리 어드바이저"""
    
    def __init__(self):
        self.knowledge_base = None
        self.multi_agent_system = None
        self.is_initialized = False
        
    def initialize(self):
        """시스템 초기화"""
        try:
            with st.spinner("🔄 시스템 초기화 중..."):
                if not FULL_FEATURES_AVAILABLE:
                    # 간단 모드로 초기화
                    st.warning("⚠️ 전체 기능 모듈을 사용할 수 없어 간단 모드로 실행합니다.")
                    self.is_initialized = True
                    st.success("✅ 간단 모드 초기화 완료!")
                    return True
                
                # 전체 기능 모드 초기화
                # 지식베이스 초기화
                self.knowledge_base = KnowledgeBase()
                kb_success = self.knowledge_base.initialize()
                
                if not kb_success:
                    st.error("❌ 지식베이스 초기화 실패")
                    return False
                
                # Multi Agent 시스템 초기화
                self.multi_agent_system = MultiAgentSystem()
                agent_success = self.multi_agent_system.initialize(self.knowledge_base)
                
                if not agent_success:
                    st.error("❌ Multi Agent 시스템 초기화 실패")
                    return False
                
                self.is_initialized = True
                st.success("✅ 전체 기능 모드 초기화 완료!")
                return True
                
        except Exception as e:
            st.error(f"❌ 초기화 중 오류 발생: {str(e)}")
            logger.error(f"초기화 오류: {e}")
            # 오류 발생 시 간단 모드로 전환
            self.is_initialized = True
            st.warning("⚠️ 오류로 인해 간단 모드로 전환합니다.")
            return True
    
    def get_financial_advice(self, user_input: str, category: str = "general") -> dict:
        """재무 상담 제공"""
        if not self.is_initialized:
            return {"error": "시스템이 초기화되지 않았습니다."}
        
        try:
            # 간단 모드인 경우 내장 로직 사용
            if not FULL_FEATURES_AVAILABLE or not hasattr(self, 'multi_agent_system') or self.multi_agent_system is None:
                return self._get_simple_advice(user_input, category)
            
            # 전체 기능 모드인 경우 에이전트 사용
            # 카테고리별 에이전트 선택
            if category == "budget":
                agent_name = "budget_agent"
            elif category == "investment":
                agent_name = "investment_agent"
            elif category == "tax":
                agent_name = "tax_agent"
            elif category == "retirement":
                agent_name = "retirement_agent"
            else:
                agent_name = "general_agent"
            
            # 에이전트 실행
            if agent_name in self.multi_agent_system.agents:
                agent = self.multi_agent_system.agents[agent_name]
                result = agent.run(user_input)
                return {
                    "success": True,
                    "response": result,
                    "category": category,
                    "timestamp": datetime.now().isoformat()
                }
            else:
                # 일반적인 응답
                return {
                    "success": True,
                    "response": f"재무 상담: {user_input}에 대한 조언을 제공합니다.",
                    "category": "general",
                    "timestamp": datetime.now().isoformat()
                }
                
        except Exception as e:
            logger.error(f"상담 처리 오류: {e}")
            # 오류 발생 시 간단 모드로 전환
            return self._get_simple_advice(user_input, category)
    
    def _get_simple_advice(self, user_input: str, category: str) -> dict:
        """간단 모드 재무 상담 제공"""
        try:
            # 카테고리별 기본 응답
            responses = {
                "budget": {
                    "title": "💰 예산 관리 조언",
                    "advice": [
                        "1. 수입의 50-30-20 법칙을 따르세요 (필수지출 50%, 선택지출 30%, 저축 20%)",
                        "2. 모든 지출을 기록하고 분류하세요",
                        "3. 월별 예산을 세우고 정기적으로 검토하세요",
                        "4. 비상금을 3-6개월 생활비만큼 확보하세요"
                    ]
                },
                "investment": {
                    "title": "📈 투자 조언",
                    "advice": [
                        "1. 분산 투자로 리스크를 줄이세요",
                        "2. 장기 투자 관점을 유지하세요",
                        "3. 정기적인 포트폴리오 리밸런싱을 하세요",
                        "4. 투자 원금의 10% 이상을 한 번에 투자하지 마세요"
                    ]
                },
                "tax": {
                    "title": "🧾 세무 조언",
                    "advice": [
                        "1. 연말정산 시 필요한 서류를 미리 준비하세요",
                        "2. 세금공제 혜택을 최대한 활용하세요",
                        "3. 투자 관련 세금 혜택을 확인하세요",
                        "4. 전문가와 상담하여 세무 계획을 수립하세요"
                    ]
                },
                "retirement": {
                    "title": "🏠 퇴직 계획 조언",
                    "advice": [
                        "1. 퇴직 후 필요 생활비를 계산하세요",
                        "2. 연금 상품을 조기에 가입하세요",
                        "3. 부동산 투자도 고려해보세요",
                        "4. 정기적으로 퇴직 계획을 점검하세요"
                    ]
                },
                "general": {
                    "title": "💡 일반 재무 조언",
                    "advice": [
                        "1. 수입과 지출을 정확히 파악하세요",
                        "2. 목표를 세우고 단계별로 실행하세요",
                        "3. 정기적으로 재무 상태를 점검하세요",
                        "4. 전문가 상담을 받아보세요"
                    ]
                }
            }
            
            selected = responses.get(category, responses["general"])
            
            # 사용자 입력에 따른 맞춤 조언 추가
            custom_advice = self._generate_custom_advice(user_input, category)
            
            return {
                "success": True,
                "title": selected["title"],
                "general_advice": selected["advice"],
                "custom_advice": custom_advice,
                "category": category,
                "mode": "simple",
                "timestamp": datetime.now().isoformat()
            }
                
        except Exception as e:
            logger.error(f"간단 상담 처리 오류: {e}")
            return {"error": f"상담 처리 중 오류 발생: {str(e)}"}
    
    def _generate_custom_advice(self, user_input: str, category: str) -> str:
        """사용자 입력에 따른 맞춤 조언 생성"""
        input_lower = user_input.lower()
        
        # 키워드 기반 맞춤 조언
        if "월급" in input_lower or "연봉" in input_lower:
            if "500" in input_lower or "500만" in input_lower:
                return "월급 500만원 기준으로는 생활비 250만원, 여유자금 150만원, 저축 100만원으로 나누어 관리하는 것을 권장합니다."
            elif "300" in input_lower or "300만" in input_lower:
                return "월급 300만원 기준으로는 생활비 180만원, 여유자금 60만원, 저축 60만원으로 관리하세요."
        
        if "투자" in input_lower:
            if "주식" in input_lower:
                return "주식 투자는 장기 관점으로 접근하고, 분산 투자를 통해 리스크를 관리하세요."
            elif "부동산" in input_lower:
                return "부동산 투자는 위치와 수익성을 중점적으로 고려하고, 정부 정책 변화에 주의하세요."
        
        if "저축" in input_lower or "적금" in input_lower:
            return "정기적금이나 자동이체를 활용하여 꾸준한 저축 습관을 만드세요."
        
        if "대출" in input_lower or "빚" in input_lower:
            return "대출은 최소한으로 유지하고, 고금리 대출부터 우선적으로 상환하세요."
        
        return "구체적인 상황에 맞는 상세한 상담을 위해 전문가와 상담하시는 것을 권장합니다."
    
    def analyze_portfolio(self, portfolio_data: dict) -> dict:
        """포트폴리오 분석"""
        if not self.is_initialized:
            return {"error": "시스템이 초기화되지 않았습니다."}
        
        try:
            # 간단 모드인 경우 내장 로직 사용
            if not FULL_FEATURES_AVAILABLE:
                return self._analyze_portfolio_simple(portfolio_data)
            
            # 전체 기능 모드인 경우 시뮬레이터 사용
            analysis = portfolio_simulator.analyze_portfolio(portfolio_data)
            return {
                "success": True,
                "analysis": analysis,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"포트폴리오 분석 오류: {e}")
            # 오류 발생 시 간단 모드로 전환
            return self._analyze_portfolio_simple(portfolio_data)
    
    def _analyze_portfolio_simple(self, portfolio_data: dict) -> dict:
        """간단 모드 포트폴리오 분석"""
        try:
            # 간단한 포트폴리오 분석
            total_value = 0
            stock_value = 0
            bond_value = 0
            cash_value = portfolio_data.get("cash", 0)
            
            # 주식 가치 계산
            for stock in portfolio_data.get("stocks", []):
                current_price = stock.get("avg_price", 0) * 1.1  # 10% 상승 가정
                stock_value += current_price * stock.get("shares", 0)
            
            # 채권 가치 계산
            for bond in portfolio_data.get("bonds", []):
                bond_value += bond.get("amount", 0)
            
            total_value = stock_value + bond_value + cash_value
            
            # 자산 배분 분석
            stock_ratio = (stock_value / total_value * 100) if total_value > 0 else 0
            bond_ratio = (bond_value / total_value * 100) if total_value > 0 else 0
            cash_ratio = (cash_value / total_value * 100) if total_value > 0 else 0
            
            # 리스크 평가
            risk_level = "보수적" if stock_ratio < 30 else "중립적" if stock_ratio < 60 else "공격적"
            
            # 추천사항
            recommendations = []
            if stock_ratio > 70:
                recommendations.append("주식 비중이 높아 리스크가 큽니다. 채권이나 현금 비중을 늘려보세요.")
            elif cash_ratio > 50:
                recommendations.append("현금 비중이 높습니다. 투자 기회를 놓치지 않도록 적절한 투자를 고려해보세요.")
            
            return {
                "success": True,
                "total_value": total_value,
                "asset_allocation": {
                    "stocks": {"value": stock_value, "ratio": stock_ratio},
                    "bonds": {"value": bond_value, "ratio": bond_ratio},
                    "cash": {"value": cash_value, "ratio": cash_ratio}
                },
                "risk_level": risk_level,
                "recommendations": recommendations,
                "mode": "simple",
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"간단 포트폴리오 분석 오류: {e}")
            return {"error": f"포트폴리오 분석 중 오류 발생: {str(e)}"}
    
    def get_market_data(self, symbol: str) -> dict:
        """시장 데이터 조회"""
        try:
            # 간단 모드인 경우 모의 데이터 사용
            if not FULL_FEATURES_AVAILABLE:
                return self._get_market_data_simple(symbol)
            
            # 전체 기능 모드인 경우 금융 데이터 모듈 사용
            data = financial_data.get_stock_data(symbol)
            return {
                "success": True,
                "data": data,
                "symbol": symbol,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"시장 데이터 조회 오류: {e}")
            # 오류 발생 시 간단 모드로 전환
            return self._get_market_data_simple(symbol)
    
    def _get_market_data_simple(self, symbol: str) -> dict:
        """간단 모드 시장 데이터 조회 (모의 데이터)"""
        try:
            # 모의 주가 데이터 생성
            import random
            base_price = 100 + random.randint(-50, 100)
            
            # 30일간의 모의 데이터
            dates = pd.date_range(start=datetime.now() - pd.Timedelta(days=30), periods=30, freq='D')
            prices = []
            
            for i in range(30):
                change = random.uniform(-0.05, 0.05)  # ±5% 변동
                if i == 0:
                    price = base_price
                else:
                    price = prices[-1] * (1 + change)
                prices.append(round(price, 2))
            
            # 거래량 데이터
            volumes = [random.randint(1000000, 5000000) for _ in range(30)]
            
            data = {
                "symbol": symbol,
                "current_price": prices[-1],
                "change": round(prices[-1] - prices[-2], 2) if len(prices) > 1 else 0,
                "change_percent": round(((prices[-1] - prices[-2]) / prices[-2] * 100), 2) if len(prices) > 1 else 0,
                "data": [
                    {
                        "date": date.strftime("%Y-%m-%d"),
                        "open": price,
                        "high": price * 1.02,
                        "low": price * 0.98,
                        "close": price,
                        "volume": volume
                    }
                    for date, price, volume in zip(dates, prices, volumes)
                ]
            }
            
            return {
                "success": True,
                "data": data,
                "note": "⚠️ 이는 모의 데이터입니다. 실제 투자 시에는 정확한 시장 데이터를 확인하세요.",
                "mode": "simple",
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"간단 시장 데이터 조회 오류: {e}")
            return {"error": f"시장 데이터 조회 중 오류 발생: {str(e)}"}

# 전역 어드바이저 인스턴스
@st.cache_resource
def get_advisor():
    """캐시된 어드바이저 인스턴스 반환"""
    advisor = DirectFinanceAdvisor()
    advisor.initialize()
    return advisor

def main():
    """메인 애플리케이션"""
    st.title("💰 AI 재무관리 어드바이저 (직접 실행)")
    st.markdown("---")
    
    # 사이드바 설정
    with st.sidebar:
        st.header("⚙️ 설정")
        
        # 카테고리 선택
        category = st.selectbox(
            "상담 카테고리",
            ["general", "budget", "investment", "tax", "retirement"],
            format_func=lambda x: {
                "general": "일반 상담",
                "budget": "예산 관리",
                "investment": "투자 상담",
                "tax": "세무 상담",
                "retirement": "퇴직 계획"
            }[x]
        )
        
        # 시스템 상태 확인
        advisor = get_advisor()
        if advisor.is_initialized:
            st.success("✅ 시스템 준비 완료")
        else:
            st.error("❌ 시스템 초기화 필요")
            if st.button("🔄 시스템 재초기화"):
                advisor.initialize()
                st.rerun()
    
    # 메인 컨텐츠
    tab1, tab2, tab3, tab4 = st.tabs(["💬 재무 상담", "📊 포트폴리오 분석", "📈 시장 데이터", "📋 사용법"])
    
    with tab1:
        st.header("💬 AI 재무 상담")
        
        # 사용자 입력
        user_input = st.text_area(
            "재무 관련 질문이나 상담 내용을 입력하세요:",
            placeholder="예: 월급 500만원인데 어떻게 투자하면 좋을까요?",
            height=100
        )
        
        if st.button("🤖 AI 상담 받기", type="primary"):
            if user_input.strip():
                with st.spinner("AI가 상담을 준비하고 있습니다..."):
                    result = advisor.get_financial_advice(user_input, category)
                    
                    if "error" in result:
                        st.error(f"❌ 오류: {result['error']}")
                    else:
                        st.success("✅ 상담 완료!")
                        
                        # 응답 표시
                        if result.get("mode") == "simple":
                            st.subheader(f"🤖 {result['title']}")
                            
                            # 맞춤 조언
                            if result.get("custom_advice"):
                                st.info(f"💡 맞춤 조언: {result['custom_advice']}")
                            
                            # 일반 조언
                            st.subheader("📋 일반적인 조언")
                            for i, advice in enumerate(result["general_advice"], 1):
                                st.write(f"{i}. {advice}")
                        else:
                            st.subheader("🤖 AI 상담 결과")
                            st.write(result["response"])
                        
                        # 메타데이터
                        with st.expander("📋 상담 정보"):
                            st.json(result)
            else:
                st.warning("⚠️ 상담 내용을 입력해주세요.")
    
    with tab2:
        st.header("📊 포트폴리오 분석")
        
        # 샘플 포트폴리오 데이터
        sample_portfolio = {
            "stocks": [
                {"symbol": "AAPL", "shares": 10, "avg_price": 150},
                {"symbol": "GOOGL", "shares": 5, "avg_price": 2800},
                {"symbol": "MSFT", "shares": 8, "avg_price": 300}
            ],
            "bonds": [
                {"name": "국채 10년", "amount": 10000000, "yield": 0.03}
            ],
            "cash": 5000000
        }
        
        # JSON 에디터 대신 텍스트 영역 사용 (하위 버전 호환성)
        st.subheader("📋 포트폴리오 데이터 입력")
        st.info("아래 JSON 데이터를 수정하여 포트폴리오를 구성하세요.")
        
        portfolio_json = st.text_area(
            "포트폴리오 데이터 (JSON 형식)",
            value=json.dumps(sample_portfolio, indent=2, ensure_ascii=False),
            height=300,
            help="JSON 형식으로 포트폴리오 데이터를 입력하세요."
        )
        
        try:
            portfolio_data = json.loads(portfolio_json)
        except json.JSONDecodeError as e:
            st.error(f"❌ JSON 형식 오류: {e}")
            st.info("기본 샘플 데이터를 사용합니다.")
            portfolio_data = sample_portfolio
        
        if st.button("📊 포트폴리오 분석", type="primary"):
            with st.spinner("포트폴리오를 분석하고 있습니다..."):
                result = advisor.analyze_portfolio(portfolio_data)
                
                if "error" in result:
                    st.error(f"❌ 오류: {result['error']}")
                else:
                    st.success("✅ 분석 완료!")
                    
                    if result.get("mode") == "simple":
                        # 간단 모드 결과 표시
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("총 자산", f"₩{result['total_value']:,.0f}")
                        with col2:
                            st.metric("리스크 수준", result['risk_level'])
                        with col3:
                            st.metric("주식 비중", f"{result['asset_allocation']['stocks']['ratio']:.1f}%")
                        
                        # 자산 배분 차트
                        if PLOTLY_AVAILABLE:
                            allocation = result['asset_allocation']
                            fig = go.Figure(data=[go.Pie(
                                labels=['주식', '채권', '현금'],
                                values=[allocation['stocks']['value'], allocation['bonds']['value'], allocation['cash']['value']],
                                hole=0.3
                            )])
                            fig.update_layout(title="자산 배분")
                            st.plotly_chart(fig)
                        
                        # 추천사항
                        if result.get('recommendations'):
                            st.subheader("💡 추천사항")
                            for rec in result['recommendations']:
                                st.info(rec)
                    else:
                        # 전체 기능 모드 결과 표시
                        st.json(result["analysis"])
    
    with tab3:
        st.header("📈 시장 데이터")
        
        col1, col2 = st.columns(2)
        
        with col1:
            symbol = st.text_input("주식 심볼", value="AAPL")
            
        with col2:
            if st.button("📈 데이터 조회", type="primary"):
                with st.spinner("시장 데이터를 조회하고 있습니다..."):
                    result = advisor.get_market_data(symbol)
                    
                    if "error" in result:
                        st.error(f"❌ 오류: {result['error']}")
                    else:
                        st.success("✅ 데이터 조회 완료!")
                        
                        data = result["data"]
                        
                        if result.get("mode") == "simple":
                            # 간단 모드 결과 표시
                            # 현재 가격 정보
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.metric("현재가", f"${data['current_price']}")
                            with col2:
                                change_color = "normal" if data['change'] >= 0 else "inverse"
                                st.metric("변동", f"${data['change']}", delta=f"{data['change_percent']}%")
                            with col3:
                                st.info(result.get("note", ""))
                            
                            # 차트 표시
                            if PLOTLY_AVAILABLE:
                                df = pd.DataFrame(data["data"])
                                fig = px.line(df, x="date", y="close", title=f"{symbol} 주가 추이 (모의 데이터)")
                                st.plotly_chart(fig)
                        else:
                            # 전체 기능 모드 결과 표시
                            if PLOTLY_AVAILABLE and "data" in result["data"]:
                                # 간단한 차트 표시
                                df = pd.DataFrame(result["data"]["data"])
                                if not df.empty:
                                    fig = px.line(df, x="date", y="close", title=f"{symbol} 주가 추이")
                                    st.plotly_chart(fig)
                        
                        # 상세 데이터
                        with st.expander("📋 상세 데이터"):
                            st.json(data)
    
    with tab4:
        st.header("📋 사용법")
        
        st.markdown("""
        ### 🚀 직접 실행 모드 사용법
        
        이 버전은 API 서버 없이 모든 기능을 직접 실행합니다.
        
        #### 💬 재무 상담
        1. **카테고리 선택**: 사이드바에서 상담 카테고리를 선택하세요
        2. **질문 입력**: 재무 관련 질문을 자유롭게 입력하세요
        3. **AI 상담**: AI가 전문적인 재무 상담을 제공합니다
        
        #### 📊 포트폴리오 분석
        1. **데이터 입력**: 포트폴리오 데이터를 JSON 형태로 입력하세요
        2. **분석 실행**: 포트폴리오 분석을 실행하여 투자 성과를 확인하세요
        
        #### 📈 시장 데이터
        1. **심볼 입력**: 조회하고 싶은 주식 심볼을 입력하세요
        2. **데이터 조회**: 실시간 시장 데이터를 확인하세요
        
        ### 🔧 주요 특징
        - ✅ API 서버 불필요
        - ✅ 빠른 응답 속도
        - ✅ 오프라인 환경에서도 사용 가능
        - ✅ 모든 기능 통합 제공
        """)

if __name__ == "__main__":
    main()
