"""
Streamlit UI 애플리케이션
AI 재무관리 어드바이저의 웹 인터페이스
"""

import streamlit as st
import requests
import json
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import time

# 페이지 설정 - 간단한 버전으로 수정
st.set_page_config(
    page_title="AI 재무관리 어드바이저",
    page_icon="💰",
    layout="wide"
)

# API 설정
API_BASE_URL = "http://localhost:8000"

# 세션 상태 초기화
if 'user_data' not in st.session_state:
    st.session_state.user_data = {}
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

def check_api_health():
    """API 서버 상태 확인"""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        return response.status_code == 200
    except:
        return False

def call_api(endpoint, data=None):
    """API 호출"""
    try:
        if data:
            response = requests.post(f"{API_BASE_URL}{endpoint}", json=data, timeout=30)
        else:
            response = requests.get(f"{API_BASE_URL}{endpoint}", timeout=30)
        
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"API 호출 실패: {response.status_code}")
            return None
    except Exception as e:
        st.error(f"API 연결 오류: {str(e)}")
        return None

def format_currency(amount):
    """통화 포맷팅"""
    return f"₩{amount:,.0f}"

def format_percentage(value):
    """백분율 포맷팅"""
    return f"{value:.2f}%"

def create_budget_chart(expenses_data):
    """예산 차트 생성"""
    if not expenses_data:
        return None
    
    categories = list(expenses_data.keys())
    amounts = list(expenses_data.values())
    
    fig = px.pie(
        values=amounts,
        names=categories,
        title="월별 지출 분포",
        color_discrete_sequence=px.colors.qualitative.Set3
    )
    
    fig.update_traces(textposition='inside', textinfo='percent+label')
    return fig

def create_portfolio_chart(allocation_data):
    """포트폴리오 차트 생성"""
    if not allocation_data:
        return None
    
    categories = []
    amounts = []
    
    for asset_type, data in allocation_data.items():
        if isinstance(data, dict) and 'amount' in data:
            categories.append(asset_type)
            amounts.append(data['amount'])
        else:
            categories.append(asset_type)
            amounts.append(data)
    
    fig = px.pie(
        values=amounts,
        names=categories,
        title="포트폴리오 배분",
        color_discrete_sequence=px.colors.qualitative.Set1
    )
    
    fig.update_traces(textposition='inside', textinfo='percent+label')
    return fig

def main():
    """메인 애플리케이션"""
    
    # 헤더
    st.title("💰 AI 재무관리 어드바이저")
    st.markdown("---")
    
    # API 상태 확인
    if not check_api_health():
        st.error("⚠️ API 서버에 연결할 수 없습니다. 서버가 실행 중인지 확인해주세요.")
        st.info("API 서버 실행 방법: `uvicorn src.api.main:app --reload`")
        return
    
    # 사이드바
    with st.sidebar:
        st.header("⚙️ 설정")
        
        # 사용자 정보 입력
        st.subheader("👤 사용자 정보")
        
        age = st.number_input("나이", min_value=18, max_value=100, value=30)
        income = st.number_input("연소득 (원)", min_value=0, value=50000000, step=1000000)
        expenses = st.number_input("연지출 (원)", min_value=0, value=30000000, step=1000000)
        savings = st.number_input("저축액 (원)", min_value=0, value=10000000, step=1000000)
        risk_tolerance = st.selectbox(
            "위험 성향",
            ["conservative", "moderate", "aggressive"],
            format_func=lambda x: {"conservative": "보수적", "moderate": "중간", "aggressive": "공격적"}[x]
        )
        
        # 월별 지출 상세
        st.subheader("📊 월별 지출 상세")
        housing = st.number_input("주거비", min_value=0, value=800000, step=100000)
        food = st.number_input("식비", min_value=0, value=500000, step=50000)
        transportation = st.number_input("교통비", min_value=0, value=300000, step=50000)
        utilities = st.number_input("통신비", min_value=0, value=200000, step=50000)
        entertainment = st.number_input("여가비", min_value=0, value=200000, step=50000)
        other = st.number_input("기타", min_value=0, value=1000000, step=100000)
        
        # 현재 투자
        st.subheader("📈 현재 투자")
        stocks = st.number_input("주식", min_value=0, value=5000000, step=1000000)
        bonds = st.number_input("채권", min_value=0, value=2000000, step=1000000)
        cash = st.number_input("현금", min_value=0, value=3000000, step=1000000)
        
        # 사용자 데이터 저장
        user_data = {
            "age": age,
            "income": income,
            "expenses": expenses,
            "savings": savings,
            "risk_tolerance": risk_tolerance,
            "monthly_expenses": {
                "housing": housing,
                "food": food,
                "transportation": transportation,
                "utilities": utilities,
                "entertainment": entertainment,
                "other": other
            },
            "current_investments": {
                "stocks": stocks,
                "bonds": bonds,
                "cash": cash
            }
        }
        
        st.session_state.user_data = user_data
        
        # 분석 버튼
        if st.button("🔍 종합 분석 실행", type="primary"):
            st.session_state.run_analysis = True
    
    # 메인 컨텐츠
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "💬 AI 상담", 
        "📊 종합 분석", 
        "💰 예산 관리", 
        "📈 투자 관리", 
        "📋 세금 관리"
    ])
    
    # 탭 1: AI 상담
    with tab1:
        st.header("💬 AI 재무 상담")
        
        # 샘플 질문
        st.subheader("💡 샘플 질문")
        sample_queries = [
            "개인 재무 관리는 어떻게 해야 하나요?",
            "투자 포트폴리오를 어떻게 구성해야 하나요?",
            "세금 절약 방법을 알려주세요",
            "은퇴 준비는 언제부터 시작해야 하나요?",
            "비상금은 얼마나 준비해야 하나요?"
        ]
        
        cols = st.columns(2)
        for i, query in enumerate(sample_queries):
            if cols[i % 2].button(query, key=f"sample_{i}"):
                st.session_state.user_query = query
        
        # 채팅 인터페이스
        st.subheader("💬 상담하기")
        
        # 채팅 히스토리 표시
        for message in st.session_state.chat_history:
            if message["role"] == "user":
                st.chat_message("user").write(message["content"])
            else:
                st.chat_message("assistant").write(message["content"])
        
        # 사용자 입력
        user_query = st.chat_input("재무 관련 질문을 입력하세요...")
        
        if user_query:
            # 사용자 메시지 표시
            st.chat_message("user").write(user_query)
            st.session_state.chat_history.append({"role": "user", "content": user_query})
            
            # AI 응답 생성
            with st.spinner("AI가 답변을 생성하고 있습니다..."):
                response_data = call_api("/query", {
                    "query": user_query,
                    "user_data": st.session_state.user_data
                })
                
                if response_data:
                    ai_response = response_data.get("response", "죄송합니다. 답변을 생성할 수 없습니다.")
                    st.chat_message("assistant").write(ai_response)
                    st.session_state.chat_history.append({"role": "assistant", "content": ai_response})
                else:
                    st.error("AI 응답을 받을 수 없습니다.")
        
        # 채팅 초기화
        if st.button("🗑️ 대화 초기화"):
            st.session_state.chat_history = []
            st.rerun()
    
    # 탭 2: 종합 분석
    with tab2:
        st.header("📊 종합 재무 분석")
        
        if st.button("🔍 분석 실행", type="primary") or st.session_state.get('run_analysis', False):
            st.session_state.run_analysis = False
            
            with st.spinner("종합 분석을 수행하고 있습니다..."):
                analysis_data = call_api("/comprehensive-analysis", {
                    "user_data": st.session_state.user_data
                })
                
                if analysis_data:
                    result = analysis_data.get("result", {})
                    
                    # 기본 재무 지표
                    st.subheader("📈 기본 재무 지표")
                    
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.metric("연소득", format_currency(st.session_state.user_data["income"]))
                    
                    with col2:
                        st.metric("연지출", format_currency(st.session_state.user_data["expenses"]))
                    
                    with col3:
                        net_income = st.session_state.user_data["income"] - st.session_state.user_data["expenses"]
                        st.metric("순소득", format_currency(net_income))
                    
                    with col4:
                        savings_rate = (net_income / st.session_state.user_data["income"]) * 100
                        st.metric("저축률", format_percentage(savings_rate))
                    
                    # 예산 분석
                    if "budget_analysis" in result:
                        st.subheader("💰 예산 분석")
                        budget_data = result["budget_analysis"]
                        
                        if "expense_analysis" in budget_data:
                            expense_data = budget_data["expense_analysis"]
                            
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                if "categories" in expense_data:
                                    fig = create_budget_chart(expense_data["categories"])
                                    if fig:
                                        st.plotly_chart(fig, use_container_width=True)
                            
                            with col2:
                                if "recommendations" in expense_data:
                                    st.write("**지출 관련 추천사항:**")
                                    for rec in expense_data["recommendations"]:
                                        st.write(f"• {rec}")
                    
                    # 투자 분석
                    if "investment_analysis" in result:
                        st.subheader("📈 투자 분석")
                        investment_data = result["investment_analysis"]
                        
                        if "portfolio" in investment_data:
                            portfolio_data = investment_data["portfolio"]
                            
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                if "allocation" in portfolio_data:
                                    fig = create_portfolio_chart(portfolio_data["allocation"])
                                    if fig:
                                        st.plotly_chart(fig, use_container_width=True)
                            
                            with col2:
                                if "recommendations" in portfolio_data:
                                    st.write("**투자 관련 추천사항:**")
                                    for rec in portfolio_data["recommendations"]:
                                        st.write(f"• {rec}")
                    
                    # 세금 분석
                    if "tax_analysis" in result:
                        st.subheader("📋 세금 분석")
                        tax_data = result["tax_analysis"]
                        
                        if "deductions" in tax_data:
                            deductions_data = tax_data["deductions"]
                            
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                if "total_deduction" in deductions_data:
                                    st.metric("총 공제액", format_currency(deductions_data["total_deduction"]))
                                
                                if "estimated_tax_savings" in deductions_data:
                                    st.metric("예상 세금 절약액", format_currency(deductions_data["estimated_tax_savings"]))
                            
                            with col2:
                                if "recommendations" in deductions_data:
                                    st.write("**세금 절약 추천사항:**")
                                    for rec in deductions_data["recommendations"]:
                                        st.write(f"• {rec}")
                    
                    # 종합 추천사항
                    if "overall_recommendations" in result:
                        st.subheader("🎯 종합 추천사항")
                        recommendations = result["overall_recommendations"]
                        
                        for i, rec in enumerate(recommendations[:5], 1):
                            st.write(f"{i}. {rec}")
                else:
                    st.error("분석 데이터를 받을 수 없습니다.")
    
    # 탭 3: 예산 관리
    with tab3:
        st.header("💰 예산 관리")
        
        if st.button("📊 예산 분석", type="primary"):
            with st.spinner("예산 분석을 수행하고 있습니다..."):
                budget_data = call_api("/analyze/budget", {
                    "analysis_type": "budget",
                    "user_data": st.session_state.user_data
                })
                
                if budget_data:
                    result = budget_data.get("result", {})
                    
                    # 예산 분석 결과
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        if "net_income" in result:
                            st.metric("순소득", format_currency(result["net_income"]))
                    
                    with col2:
                        if "savings_rate" in result:
                            st.metric("저축률", format_percentage(result["savings_rate"]))
                    
                    with col3:
                        if "health_score" in result:
                            st.metric("재무 건강도", f"{result['health_score']:.0f}/100")
                    
                    # 지출 분석
                    if "expense_analysis" in result:
                        expense_data = result["expense_analysis"]
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            if "categories" in expense_data:
                                fig = create_budget_chart(expense_data["categories"])
                                if fig:
                                    st.plotly_chart(fig, use_container_width=True)
                        
                        with col2:
                            if "recommendations" in expense_data:
                                st.write("**예산 관련 추천사항:**")
                                for rec in expense_data["recommendations"]:
                                    st.write(f"• {rec}")
                else:
                    st.error("예산 분석 데이터를 받을 수 없습니다.")
    
    # 탭 4: 투자 관리
    with tab4:
        st.header("📈 투자 관리")
        
        if st.button("📊 포트폴리오 분석", type="primary"):
            with st.spinner("투자 분석을 수행하고 있습니다..."):
                investment_data = call_api("/analyze/investment", {
                    "analysis_type": "investment",
                    "user_data": st.session_state.user_data
                })
                
                if investment_data:
                    result = investment_data.get("result", {})
                    
                    # 포트폴리오 분석
                    if "portfolio_analysis" in result:
                        portfolio_data = result["portfolio_analysis"]
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            if "allocation" in portfolio_data:
                                fig = create_portfolio_chart(portfolio_data["allocation"])
                                if fig:
                                    st.plotly_chart(fig, use_container_width=True)
                        
                        with col2:
                            if "total_value" in portfolio_data:
                                st.metric("총 투자 금액", format_currency(portfolio_data["total_value"]))
                            
                            if "risk_score" in portfolio_data:
                                risk_score = portfolio_data["risk_score"]
                                st.metric("위험도 점수", f"{risk_score:.2f}")
                        
                        if "recommendations" in portfolio_data:
                            st.write("**투자 관련 추천사항:**")
                            for rec in portfolio_data["recommendations"]:
                                st.write(f"• {rec}")
                else:
                    st.error("투자 분석 데이터를 받을 수 없습니다.")
    
    # 탭 5: 세금 관리
    with tab5:
        st.header("📋 세금 관리")
        
        if st.button("📊 세금 분석", type="primary"):
            with st.spinner("세금 분석을 수행하고 있습니다..."):
                tax_data = call_api("/analyze/tax", {
                    "analysis_type": "tax",
                    "user_data": st.session_state.user_data
                })
                
                if tax_data:
                    result = tax_data.get("result", {})
                    
                    # 세금공제 분석
                    if "tax_deductions" in result:
                        deductions_data = result["tax_deductions"]
                        
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            if "total_deduction" in deductions_data:
                                st.metric("총 공제액", format_currency(deductions_data["total_deduction"]))
                        
                        with col2:
                            if "estimated_tax_savings" in deductions_data:
                                st.metric("예상 세금 절약액", format_currency(deductions_data["estimated_tax_savings"]))
                        
                        with col3:
                            if "basic_deduction" in deductions_data:
                                st.metric("기본공제", format_currency(deductions_data["basic_deduction"]))
                        
                        if "recommendations" in deductions_data:
                            st.write("**세금 절약 추천사항:**")
                            for rec in deductions_data["recommendations"]:
                                st.write(f"• {rec}")
                else:
                    st.error("세금 분석 데이터를 받을 수 없습니다.")

if __name__ == "__main__":
    main()
