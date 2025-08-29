#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
고급 Tool Calling & Agent Executor Streamlit UI
LangChain의 Tool Calling & Agent Executor 기능을 활용한 고급 웹 인터페이스
"""

import streamlit as st
import requests
import json
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import time

# 페이지 설정
st.set_page_config(
    page_title="AI 재무관리 어드바이저 (고급 Tool Calling)",
    page_icon="🛠️",
    layout="wide"
)

# API 설정
API_BASE_URL = "http://localhost:8000"

# 세션 상태 초기화
if 'advanced_tool_chat_history' not in st.session_state:
    st.session_state.advanced_tool_chat_history = []
if 'user_data' not in st.session_state:
    st.session_state.user_data = {}
if 'is_loading' not in st.session_state:
    st.session_state.is_loading = False

def call_advanced_tool_api(endpoint, data=None):
    """고급 Tool Calling API 호출"""
    try:
        if data:
            response = requests.post(f"{API_BASE_URL}/advanced-tools{endpoint}", json=data, timeout=30)
        else:
            response = requests.get(f"{API_BASE_URL}/advanced-tools{endpoint}", timeout=30)
        
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

def main():
    """메인 함수"""
    st.title("🛠️ AI 재무관리 어드바이저 (고급 Tool Calling)")
    st.markdown("---")
    
    # 사이드바 - 사용자 정보 입력
    with st.sidebar:
        st.header("👤 사용자 정보")
        
        # 기본 정보 입력
        user_id = st.text_input("사용자 ID", value="12345")
        age = st.number_input("나이", min_value=18, max_value=100, value=30)
        income = st.number_input("연소득 (원)", min_value=0, value=50000000, step=1000000)
        expenses = st.number_input("연지출 (원)", min_value=0, value=30000000, step=1000000)
        savings = st.number_input("저축액 (원)", min_value=0, value=10000000, step=1000000)
        risk_tolerance = st.selectbox(
            "위험 성향",
            ["conservative", "moderate", "aggressive"],
            index=1
        )
        
        # 사용자 데이터 업데이트
        st.session_state.user_data = {
            "user_id": user_id,
            "age": age,
            "income": income,
            "expenses": expenses,
            "savings": savings,
            "risk_tolerance": risk_tolerance
        }
        
        st.markdown("---")
        
        # 고급 Tool Calling 기능 상태 확인
        if st.button("🔍 고급 Tool Calling 상태 확인", disabled=st.session_state.is_loading):
            status = call_advanced_tool_api("/status")
            if status:
                st.success("✅ 고급 Tool Calling 기능 정상 작동")
                st.json(status)
            else:
                st.error("❌ 고급 Tool Calling 기능 연결 실패")
    
    # 메인 탭
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "🔧 기본 Tool Calling", 
        "🤖 Agent Executor", 
        "📊 종합 재무 분석", 
        "💬 대화형 상담", 
        "🧪 개별 도구 테스트",
        "📈 결과 시각화"
    ])
    
    # 탭 1: 기본 Tool Calling
    with tab1:
        st.header("🔧 기본 Tool Calling")
        st.info("@tool 데코레이터와 bind_tools()를 사용한 기본 Tool Calling")
        
        # 샘플 질문들
        sample_queries = [
            "ID '12345' 사용자 정보를 조회해주세요.",
            "연소득 5000만원, 지출 3000만원, 저축 1000만원일 때 예산 분석을 해주세요.",
            "30세, moderate 위험성향, 1000만원 투자금액으로 투자 권장사항을 알려주세요.",
            "연소득 5000만원에 신용카드 100만원, 의료비 50만원 공제 시 세금 절약 효과는?",
            "KOSPI와 S&P 500 시장 분석을 해주세요."
        ]
        
        cols = st.columns(2)
        for i, query in enumerate(sample_queries):
            if cols[i % 2].button(query, key=f"basic_tool_{i}"):
                st.session_state.basic_tool_query = query
        
        # 기본 Tool Calling 인터페이스
        basic_query = st.text_input("질문을 입력하세요:", key="basic_tool_input")
        
        if st.button("🔧 기본 Tool Calling 실행", type="primary", disabled=st.session_state.is_loading) or st.session_state.get('basic_tool_query'):
            if basic_query or st.session_state.get('basic_tool_query'):
                query = basic_query or st.session_state.get('basic_tool_query')
                
                with st.spinner("기본 Tool Calling 실행 중..."):
                    response = call_advanced_tool_api("/basic-tool-calling", {
                        "query": query
                    })
                
                if response:
                    st.success("✅ 기본 Tool Calling 완료!")
                    
                    col1, col2 = st.columns([2, 1])
                    with col1:
                        st.subheader("🤖 AI 응답")
                        st.write(response["response"])
                    
                    with col2:
                        st.subheader("📋 실행 정보")
                        st.write(f"**방법**: {response['method']}")
                        st.write(f"**시간**: {response['timestamp']}")
                        
                        if response.get("tool_calls"):
                            st.write("**호출된 도구**:")
                            for tool_call in response["tool_calls"]:
                                st.write(f"- {tool_call.get('name', 'Unknown')}")
                
                st.session_state.basic_tool_query = None
    
    # 탭 2: Agent Executor
    with tab2:
        st.header("🤖 Agent Executor")
        st.info("create_tool_calling_agent와 AgentExecutor를 사용한 고급 질의 처리")
        
        # 샘플 질문들
        agent_queries = [
            "12345번 사용자 정보 좀 알려줘!",
            "내 재무 상황을 종합적으로 분석해주세요.",
            "투자 포트폴리오를 추천해주고 시장 상황도 함께 알려주세요.",
            "세금 절약 방법과 예산 관리를 동시에 조언해주세요."
        ]
        
        cols = st.columns(2)
        for i, query in enumerate(agent_queries):
            if cols[i % 2].button(query, key=f"agent_exec_{i}"):
                st.session_state.agent_exec_query = query
        
        # Agent Executor 인터페이스
        agent_query = st.text_input("질문을 입력하세요:", key="agent_exec_input")
        
        if st.button("🤖 Agent Executor 실행", type="primary", disabled=st.session_state.is_loading) or st.session_state.get('agent_exec_query'):
            if agent_query or st.session_state.get('agent_exec_query'):
                query = agent_query or st.session_state.get('agent_exec_query')
                
                with st.spinner("Agent Executor 실행 중..."):
                    response = call_advanced_tool_api("/agent-executor", {
                        "query": query
                    })
                
                if response:
                    st.success("✅ Agent Executor 완료!")
                    
                    col1, col2 = st.columns([2, 1])
                    with col1:
                        st.subheader("🤖 AI 응답")
                        st.write(response["response"])
                    
                    with col2:
                        st.subheader("📋 실행 정보")
                        st.write(f"**방법**: {response['method']}")
                        st.write(f"**시간**: {response['timestamp']}")
                        
                        if response.get("intermediate_steps"):
                            st.write("**중간 단계**:")
                            for i, step in enumerate(response["intermediate_steps"], 1):
                                st.write(f"{i}. {step.get('action', {}).get('tool', 'Unknown')}")
                
                st.session_state.agent_exec_query = None
    
    # 탭 3: 종합 재무 분석
    with tab3:
        st.header("📊 종합 재무 분석")
        st.info("모든 도구를 활용한 종합적인 재무 분석")
        
        analysis_user_id = st.text_input("분석할 사용자 ID:", value="12345")
        
        if st.button("📊 종합 재무 분석 실행", type="primary", disabled=st.session_state.is_loading):
            with st.spinner("종합 재무 분석을 수행하고 있습니다..."):
                response = call_advanced_tool_api("/comprehensive-analysis", {
                    "user_id": analysis_user_id
                })
            
            if response:
                st.success("✅ 종합 재무 분석 완료!")
                
                analysis = response["analysis"]
                
                # 사용자 정보
                st.subheader("👤 사용자 정보")
                user_info = analysis.get("user_info", {})
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("이름", user_info.get("name", "N/A"))
                    st.metric("나이", f"{user_info.get('age', 0)}세")
                
                with col2:
                    st.metric("연소득", format_currency(user_info.get("income", 0)))
                    st.metric("연지출", format_currency(user_info.get("expenses", 0)))
                
                with col3:
                    st.metric("저축액", format_currency(user_info.get("savings", 0)))
                    st.metric("위험 성향", user_info.get("risk_tolerance", "N/A"))
                
                with col4:
                    portfolio = user_info.get("investment_portfolio", {})
                    st.metric("주식", format_currency(portfolio.get("stocks", 0)))
                    st.metric("채권", format_currency(portfolio.get("bonds", 0)))
                
                # 예산 분석
                st.subheader("💰 예산 분석")
                budget_analysis = analysis.get("budget_analysis", {})
                col1, col2 = st.columns(2)
                
                with col1:
                    st.metric("순소득", format_currency(budget_analysis.get("net_income", 0)))
                    st.metric("저축률", format_percentage(budget_analysis.get("savings_rate", 0)))
                    st.metric("비상금 개월수", f"{budget_analysis.get('emergency_fund_months', 0):.1f}개월")
                    st.metric("재무 건강도", f"{budget_analysis.get('health_score', 0):.0f}점")
                
                with col2:
                    if budget_analysis.get("recommendations"):
                        st.write("**추천사항**:")
                        for rec in budget_analysis["recommendations"]:
                            st.write(f"• {rec}")
                
                # 투자 권장사항
                st.subheader("📈 투자 권장사항")
                investment_rec = analysis.get("investment_recommendation", {})
                col1, col2 = st.columns(2)
                
                with col1:
                    allocation = investment_rec.get("allocation", {})
                    st.metric("주식 비율", format_percentage(allocation.get("stocks", 0)))
                    st.metric("채권 비율", format_percentage(allocation.get("bonds", 0)))
                    st.metric("현금 비율", format_percentage(allocation.get("cash", 0)))
                    st.metric("예상 수익률", format_percentage(investment_rec.get("expected_return", 0)))
                
                with col2:
                    if investment_rec.get("recommendations"):
                        st.write("**추천 상품**:")
                        for rec in investment_rec["recommendations"]:
                            st.write(f"• {rec}")
                
                # 세금 절약 효과
                st.subheader("💰 세금 절약 효과")
                tax_savings = analysis.get("tax_savings", {})
                col1, col2 = st.columns(2)
                
                with col1:
                    st.metric("과세표준", format_currency(tax_savings.get("taxable_income", 0)))
                    st.metric("세금", format_currency(tax_savings.get("tax_amount", 0)))
                    st.metric("절약 효과", format_currency(tax_savings.get("tax_savings", 0)))
                    st.metric("실효세율", format_percentage(tax_savings.get("effective_tax_rate", 0)))
                
                with col2:
                    deductions = tax_savings.get("deductions_used", {})
                    if deductions:
                        st.write("**사용된 공제**:")
                        for category, amount in deductions.items():
                            st.write(f"• {category}: {format_currency(amount)}")
    
    # 탭 4: 대화형 상담
    with tab4:
        st.header("💬 대화형 상담")
        st.info("Agent Executor를 활용한 대화형 재무 상담")
        
        # 대화 히스토리 표시
        st.subheader("💬 대화 기록")
        for i, message in enumerate(st.session_state.advanced_tool_chat_history):
            if message["role"] == "user":
                st.chat_message("user").write(message["content"])
            else:
                st.chat_message("assistant").write(message["content"])
        
        # 새로운 메시지 입력
        new_message = st.chat_input("메시지를 입력하세요...")
        
        if new_message:
            # 사용자 메시지 추가
            st.session_state.advanced_tool_chat_history.append({
                "role": "user",
                "content": new_message
            })
            
            # AI 응답 생성
            with st.spinner("대화형 상담 중..."):
                response = call_advanced_tool_api("/interactive-consultation", {
                    "query": new_message,
                    "chat_history": st.session_state.advanced_tool_chat_history[:-1]
                })
            
            if response:
                # AI 응답 추가
                st.session_state.advanced_tool_chat_history.append({
                    "role": "assistant",
                    "content": response["response"]
                })
                
                # 페이지 새로고침
                st.rerun()
        
        # 대화 초기화
        if st.button("🗑️ 대화 초기화", disabled=st.session_state.is_loading):
            st.session_state.advanced_tool_chat_history = []
            st.rerun()
    
    # 탭 5: 개별 도구 테스트
    with tab5:
        st.header("🧪 개별 도구 테스트")
        st.info("각 도구를 개별적으로 테스트")
        
        tool_name = st.selectbox(
            "테스트할 도구 선택",
            [
                "get_user_financial_info",
                "calculate_budget_analysis",
                "get_investment_recommendation",
                "calculate_tax_savings",
                "get_market_analysis"
            ]
        )
        
        # 도구별 파라미터 입력
        if tool_name == "get_user_financial_info":
            user_id = st.text_input("사용자 ID", value="12345")
            parameters = {"user_id": user_id}
        
        elif tool_name == "calculate_budget_analysis":
            col1, col2, col3 = st.columns(3)
            with col1:
                income = st.number_input("연소득", value=50000000, step=1000000)
            with col2:
                expenses = st.number_input("연지출", value=30000000, step=1000000)
            with col3:
                savings = st.number_input("저축액", value=10000000, step=1000000)
            parameters = {"income": income, "expenses": expenses, "savings": savings}
        
        elif tool_name == "get_investment_recommendation":
            col1, col2, col3 = st.columns(3)
            with col1:
                age = st.number_input("나이", value=30, min_value=18, max_value=100)
            with col2:
                risk_tolerance = st.selectbox("위험 성향", ["conservative", "moderate", "aggressive"])
            with col3:
                investment_amount = st.number_input("투자 금액", value=10000000, step=1000000)
            parameters = {"age": age, "risk_tolerance": risk_tolerance, "investment_amount": investment_amount}
        
        elif tool_name == "calculate_tax_savings":
            col1, col2 = st.columns(2)
            with col1:
                income = st.number_input("연소득", value=50000000, step=1000000)
            with col2:
                deductions = {
                    "신용카드": st.number_input("신용카드", value=1000000, step=100000),
                    "의료비": st.number_input("의료비", value=500000, step=100000),
                    "보험료": st.number_input("보험료", value=300000, step=100000)
                }
            parameters = {"income": income, "deductions": deductions}
        
        elif tool_name == "get_market_analysis":
            symbols = st.multiselect(
                "분석할 지수",
                ["^KS11", "^GSPC", "^IXIC"],
                default=["^KS11", "^GSPC"]
            )
            parameters = {"symbols": symbols}
        
        if st.button("🧪 도구 테스트 실행", type="primary", disabled=st.session_state.is_loading):
            with st.spinner("도구 테스트 중..."):
                response = call_advanced_tool_api("/tool-test", {
                    "tool_name": tool_name,
                    "parameters": parameters
                })
            
            if response:
                st.success("✅ 도구 테스트 완료!")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.subheader("📋 테스트 결과")
                    st.json(response["result"])
                
                with col2:
                    st.subheader("📊 테스트 정보")
                    st.write(f"**도구**: {response['tool_name']}")
                    st.write(f"**파라미터**: {response['parameters']}")
                    st.write(f"**방법**: {response['method']}")
                    st.write(f"**시간**: {response['timestamp']}")
    
    # 탭 6: 결과 시각화
    with tab6:
        st.header("📈 결과 시각화")
        st.info("분석 결과를 차트로 시각화")
        
        # 시각화 옵션
        viz_option = st.selectbox(
            "시각화 옵션",
            ["예산 분석", "투자 배분", "세금 절약 효과", "시장 분석"]
        )
        
        if viz_option == "예산 분석":
            # 예산 분석 차트
            st.subheader("💰 예산 분석 차트")
            
            # 샘플 데이터
            budget_data = {
                "연소득": 50000000,
                "연지출": 30000000,
                "저축액": 10000000
            }
            
            fig = px.pie(
                values=list(budget_data.values()),
                names=list(budget_data.keys()),
                title="수입 대비 지출 및 저축 비율"
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # 재무 건강도 게이지
            health_score = 75
            fig = go.Figure(go.Indicator(
                mode="gauge+number+delta",
                value=health_score,
                domain={'x': [0, 1], 'y': [0, 1]},
                title={'text': "재무 건강도 점수"},
                gauge={'axis': {'range': [None, 100]},
                       'bar': {'color': "darkblue"},
                       'steps': [{'range': [0, 50], 'color': "lightgray"},
                                {'range': [50, 75], 'color': "yellow"},
                                {'range': [75, 100], 'color': "green"}]}
            ))
            st.plotly_chart(fig, use_container_width=True)
        
        elif viz_option == "투자 배분":
            # 투자 배분 차트
            st.subheader("📈 투자 배분 차트")
            
            # 샘플 데이터
            allocation_data = {
                "주식": 50,
                "채권": 30,
                "현금": 20
            }
            
            fig = px.pie(
                values=list(allocation_data.values()),
                names=list(allocation_data.keys()),
                title="자산 배분 비율"
            )
            st.plotly_chart(fig, use_container_width=True)
        
        elif viz_option == "세금 절약 효과":
            # 세금 절약 효과 차트
            st.subheader("💰 세금 절약 효과 차트")
            
            # 샘플 데이터
            tax_data = {
                "공제 전 세금": 8000000,
                "공제 후 세금": 6000000,
                "절약 효과": 2000000
            }
            
            fig = px.bar(
                x=list(tax_data.keys()),
                y=list(tax_data.values()),
                title="세금 절약 효과 비교",
                color=list(tax_data.keys()),
                color_discrete_map={
                    "공제 전 세금": "red",
                    "공제 후 세금": "orange", 
                    "절약 효과": "green"
                }
            )
            st.plotly_chart(fig, use_container_width=True)
        
        elif viz_option == "시장 분석":
            # 시장 분석 차트
            st.subheader("📊 시장 분석 차트")
            
            # 샘플 데이터
            market_data = {
                "KOSPI": [2500, 1.2],
                "S&P 500": [4500, -0.5],
                "NASDAQ": [14000, 0.8]
            }
            
            fig = px.bar(
                x=list(market_data.keys()),
                y=[data[1] for data in market_data.values()],
                title="주요 지수 변동률 (%)",
                color=[data[1] for data in market_data.values()],
                color_continuous_scale="RdYlGn"
            )
            st.plotly_chart(fig, use_container_width=True)

if __name__ == "__main__":
    main()
