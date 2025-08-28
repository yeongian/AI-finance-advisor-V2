#!/usr/bin/env python3
"""
간단한 AI 재무관리 어드바이저 Streamlit 앱
"""

import streamlit as st
import requests
import json
from datetime import datetime

# 페이지 설정
st.set_page_config(
    page_title="AI 재무관리 어드바이저",
    page_icon="💰",
    layout="wide"
)

# API 설정
API_BASE_URL = "http://localhost:8000"

# 세션 상태 초기화
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'user_query' not in st.session_state:
    st.session_state.user_query = ""

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
            return None
    except Exception as e:
        return None

def format_currency(amount):
    """통화 포맷팅"""
    return f"₩{amount:,.0f}"

def set_sample_question(question):
    """샘플 질문을 텍스트 입력란에 설정"""
    st.session_state.user_query = question

# 메인 앱
def main():
    st.title("💰 AI 재무관리 어드바이저")
    st.markdown("---")
    
    # API 상태 확인
    api_healthy = check_api_health()
    
    if not api_healthy:
        st.error("⚠️ API 서버에 연결할 수 없습니다. API 서버가 실행 중인지 확인해주세요.")
        st.info("API 서버 실행: `py -m uvicorn src.api.main:app --host localhost --port 8000`")
        return
    
    st.success("✅ API 서버에 연결되었습니다!")
    
    # 탭 생성
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["💬 AI 상담", "📊 종합 분석", "💰 예산 관리", "📈 투자 관리", "🧾 세금 관리"])
    
    with tab1:
        st.header("💬 AI 재무 상담")
        
        # 샘플 질문
        st.subheader("💡 샘플 질문")
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("개인 재무 관리는 어떻게 해야 하나요?"):
                set_sample_question("개인 재무 관리는 어떻게 해야 하나요?")
                st.rerun()
            
            if st.button("세금 절약 방법을 알려주세요"):
                set_sample_question("세금 절약 방법을 알려주세요")
                st.rerun()
            
            if st.button("비상금은 얼마나 준비해야 하나요?"):
                set_sample_question("비상금은 얼마나 준비해야 하나요?")
                st.rerun()
        
        with col2:
            if st.button("투자 포트폴리오를 어떻게 구성해야 하나요?"):
                set_sample_question("투자 포트폴리오를 어떻게 구성해야 하나요?")
                st.rerun()
            
            if st.button("은퇴 준비는 언제부터 시작해야 하나요?"):
                set_sample_question("은퇴 준비는 언제부터 시작해야 하나요?")
                st.rerun()
        
        # 상담하기
        st.subheader("💬 상담하기")
        
        # 사용자 입력
        user_query = st.text_input("질문을 입력하세요:", value=st.session_state.user_query, placeholder="예: 예산 관리는 어떻게 해야 하나요?")
        
        if st.button("질문하기"):
            if user_query:
                # API 호출
                api_response = call_api("/query", {"query": user_query})
                
                if api_response and "response" in api_response:
                    ai_answer = api_response["response"]["answer"]
                else:
                    ai_answer = "죄송합니다. 현재 서버에 문제가 있어 답변을 받을 수 없습니다. 잠시 후 다시 시도해주세요."
                
                st.session_state.chat_history.append({"user": user_query, "ai": ai_answer})
                st.session_state.user_query = ""  # 입력란 초기화
                st.rerun()
        
        # 대화 기록 표시
        if st.session_state.chat_history:
            st.subheader("📝 대화 기록")
            for i, chat in enumerate(st.session_state.chat_history):
                with st.expander(f"질문 {i+1}: {chat['user'][:50]}..."):
                    st.write(f"**질문:** {chat['user']}")
                    st.write(f"**답변:** {chat['ai']}")
        
        # 대화 초기화
        if st.button("🗑️ 대화 초기화"):
            st.session_state.chat_history = []
            st.session_state.user_query = ""
            st.rerun()
    
    with tab2:
        st.header("📊 종합 재무 분석")
        
        # 사용자 정보 입력
        st.subheader("👤 사용자 정보 입력")
        
        col1, col2 = st.columns(2)
        
        with col1:
            age = st.number_input("나이", min_value=18, max_value=100, value=30)
            income = st.number_input("연소득 (원)", min_value=0, value=50000000, step=1000000)
            expenses = st.number_input("연지출 (원)", min_value=0, value=30000000, step=1000000)
        
        with col2:
            savings = st.number_input("현재 저축액 (원)", min_value=0, value=10000000, step=1000000)
            risk_tolerance = st.selectbox("위험 성향", ["보수적", "보통", "공격적"], index=1)
        
        # 종합 분석 실행 버튼
        if st.button("🚀 종합 분석 실행", type="primary"):
            with st.spinner("분석 중입니다..."):
                user_data = {
                    "age": age,
                    "income": income,
                    "expenses": expenses,
                    "savings": savings,
                    "risk_tolerance": risk_tolerance
                }
                
                # API 호출
                analysis_result = call_api("/comprehensive-analysis", {"user_data": user_data})
                
                if analysis_result and "result" in analysis_result:
                    result = analysis_result["result"]
                    
                    st.success("✅ 분석이 완료되었습니다!")
                    
                    # 예산 분석
                    st.subheader("💰 예산 분석")
                    budget = result.get("budget_analysis", {})
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("순수입", format_currency(budget.get("net_income", 0)))
                    with col2:
                        st.metric("저축률", f"{budget.get('savings_rate', 0):.1f}%")
                    with col3:
                        st.metric("비상금 (개월)", f"{budget.get('emergency_fund_months', 0):.1f}개월")
                    
                    # 예산 추천사항
                    if "recommendations" in budget:
                        st.write("**💡 예산 관리 추천사항:**")
                        for rec in budget["recommendations"]:
                            st.write(f"• {rec}")
                    
                    st.markdown("---")
                    
                    # 투자 분석
                    st.subheader("📈 투자 분석")
                    investment = result.get("investment_analysis", {})
                    allocation = investment.get("recommended_allocation", {})
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("주식 비율", f"{allocation.get('stocks', 0):.1f}%")
                    with col2:
                        st.metric("채권 비율", f"{allocation.get('bonds', 0):.1f}%")
                    with col3:
                        st.metric("현금 비율", f"{allocation.get('cash', 0):.1f}%")
                    
                    # 투자 추천사항
                    if "recommendations" in investment:
                        st.write("**💡 투자 추천사항:**")
                        for rec in investment["recommendations"]:
                            st.write(f"• {rec}")
                    
                    st.markdown("---")
                    
                    # 세금 분석
                    st.subheader("🧾 세금 분석")
                    tax = result.get("tax_analysis", {})
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.metric("총 공제액", format_currency(tax.get("total_deduction", 0)))
                    with col2:
                        st.metric("추정 절약액", format_currency(tax.get("estimated_tax_savings", 0)))
                    
                    # 세금 추천사항
                    if "recommendations" in tax:
                        st.write("**💡 절세 전략:**")
                        for rec in tax["recommendations"]:
                            st.write(f"• {rec}")
                    
                    st.markdown("---")
                    
                    # 은퇴 분석
                    st.subheader("👴 은퇴 분석")
                    retirement = result.get("retirement_analysis", {})
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.metric("은퇴까지 남은 기간", f"{retirement.get('years_to_retirement', 0)}년")
                    with col2:
                        st.metric("총 필요 금액", format_currency(retirement.get("total_retirement_needs", 0)))
                    
                    if retirement.get("monthly_savings_needed", 0) > 0:
                        st.info(f"💡 월 저축 필요액: {format_currency(retirement.get('monthly_savings_needed', 0))}")
                    else:
                        st.success("✅ 현재 저축액으로 은퇴 목표를 달성할 수 있습니다!")
                    
                    # 은퇴 추천사항
                    if "recommendations" in retirement:
                        st.write("**💡 은퇴 준비 추천사항:**")
                        for rec in retirement["recommendations"]:
                            st.write(f"• {rec}")
                    
                    # 분석 요약
                    st.markdown("---")
                    st.subheader("📋 분석 요약")
                    
                    summary_data = {
                        "분석 항목": ["예산 관리", "투자 관리", "세금 관리", "은퇴 계획"],
                        "현재 상태": [
                            f"저축률 {budget.get('savings_rate', 0):.1f}%",
                            f"주식 {allocation.get('stocks', 0):.1f}%",
                            f"절약액 {format_currency(tax.get('estimated_tax_savings', 0))}",
                            f"{retirement.get('years_to_retirement', 0)}년 남음"
                        ]
                    }
                    
                    st.table(summary_data)
                    
                else:
                    st.error("❌ 분석 중 오류가 발생했습니다. 다시 시도해주세요.")
                    st.info("💡 API 서버가 정상적으로 실행 중인지 확인해주세요.")
    
    with tab3:
        st.header("💰 예산 관리")
        st.info("예산 관리 기능은 종합 분석 탭에서 확인할 수 있습니다.")
    
    with tab4:
        st.header("📈 투자 관리")
        st.info("투자 관리 기능은 종합 분석 탭에서 확인할 수 있습니다.")
    
    with tab5:
        st.header("🧾 세금 관리")
        st.info("세금 관리 기능은 종합 분석 탭에서 확인할 수 있습니다.")

if __name__ == "__main__":
    main()
