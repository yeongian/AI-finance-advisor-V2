#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LangGraph Streamlit UI
LangGraph의 모든 기능을 활용한 고급 웹 인터페이스
"""

import streamlit as st
import requests
import json
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import time
import uuid

# 페이지 설정
st.set_page_config(
    page_title="AI 재무관리 어드바이저 (LangGraph)",
    page_icon="🔄",
    layout="wide"
)

# API 설정
API_BASE_URL = "http://localhost:8000"

# 세션 상태 초기화
if 'langgraph_chat_history' not in st.session_state:
    st.session_state.langgraph_chat_history = []
if 'current_thread_id' not in st.session_state:
    st.session_state.current_thread_id = f"user_{uuid.uuid4().hex[:8]}"
if 'expert_consultations' not in st.session_state:
    st.session_state.expert_consultations = {}
if 'is_loading' not in st.session_state:
    st.session_state.is_loading = False

def call_langgraph_api(endpoint, data=None):
    """LangGraph API 호출"""
    try:
        if data:
            response = requests.post(f"{API_BASE_URL}/langgraph{endpoint}", json=data, timeout=30)
        else:
            response = requests.get(f"{API_BASE_URL}/langgraph{endpoint}", timeout=30)
        
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
    st.title("🔄 AI 재무관리 어드바이저 (LangGraph)")
    st.markdown("---")
    
    # 사이드바 - 설정 및 정보
    with st.sidebar:
        st.header("⚙️ 설정")
        
        # 스레드 ID 설정
        thread_id = st.text_input("스레드 ID", value=st.session_state.current_thread_id)
        if thread_id != st.session_state.current_thread_id:
            st.session_state.current_thread_id = thread_id
            st.session_state.langgraph_chat_history = []
        
        # 새 스레드 생성
        if st.button("🆕 새 스레드 생성", disabled=st.session_state.is_loading):
            st.session_state.current_thread_id = f"user_{uuid.uuid4().hex[:8]}"
            st.session_state.langgraph_chat_history = []
            st.rerun()
        
        st.markdown("---")
        
        # LangGraph 상태 확인
        if st.button("🔍 LangGraph 상태 확인", disabled=st.session_state.is_loading):
            status = call_langgraph_api("/status")
            if status:
                if status.get("langgraph_available", False):
                    st.success("✅ LangGraph 기능 정상 작동")
                else:
                    st.warning("⚠️ LangGraph 패키지가 설치되지 않았습니다")
                st.json(status)
            else:
                st.error("❌ LangGraph 기능 연결 실패")
        
        st.markdown("---")
        
        # 스레드 목록
        st.subheader("📝 스레드 목록")
        threads = call_langgraph_api("/threads")
        if threads:
            for thread in threads.get("threads", []):
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write(f"**{thread['thread_id']}**")
                    st.caption(f"메시지: {thread['message_count']}개")
                with col2:
                    if st.button("🗑️", key=f"del_{thread['thread_id']}", disabled=st.session_state.is_loading):
                        call_langgraph_api(f"/threads/{thread['thread_id']}", method="DELETE")
                        st.rerun()
    
    # 메인 탭
    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
        "💬 기본 챗봇", 
        "🛠️ Tool Agent", 
        "🤖 Multi Agent", 
        "📊 종합 분석", 
        "💭 대화형 상담", 
        "👨‍💼 전문가 상담",
        "📈 시각화"
    ])
    
    # 탭 1: 기본 챗봇
    with tab1:
        st.header("💬 기본 LangGraph 챗봇")
        st.info("LangGraph 기본 구조를 사용한 챗봇")
        
        # 샘플 메시지들
        sample_messages = [
            "안녕하세요! 재무관리에 대해 궁금한 점이 있습니다.",
            "저축하는 방법을 알려주세요.",
            "투자에 대해 조언해주세요.",
            "세금 절약 방법을 알려주세요."
        ]
        
        cols = st.columns(2)
        for i, message in enumerate(sample_messages):
            if cols[i % 2].button(message, key=f"basic_chat_{i}"):
                st.session_state.basic_chat_message = message
        
        # 기본 챗봇 인터페이스
        basic_message = st.text_input("메시지를 입력하세요:", key="basic_chat_input")
        
        if st.button("💬 기본 챗봇 실행", type="primary", disabled=st.session_state.is_loading) or st.session_state.get('basic_chat_message'):
            if basic_message or st.session_state.get('basic_chat_message'):
                message = basic_message or st.session_state.get('basic_chat_message')
                
                with st.spinner("기본 챗봇 실행 중..."):
                    response = call_langgraph_api("/basic-chat", {
                        "message": message
                    })
                
                if response:
                    st.success("✅ 기본 챗봇 완료!")
                    
                    col1, col2 = st.columns([2, 1])
                    with col1:
                        st.subheader("🤖 AI 응답")
                        st.write(response["response"])
                    
                    with col2:
                        st.subheader("📋 실행 정보")
                        st.write(f"**방법**: {response['method']}")
                        st.write(f"**시간**: {response['timestamp']}")
                
                st.session_state.basic_chat_message = None
    
    # 탭 2: Tool Agent
    with tab2:
        st.header("🛠️ LangGraph Tool Agent")
        st.info("LangGraph 기반 Tool Agent")
        
        # 샘플 질문들
        tool_queries = [
            "사용자 ID '12345'의 재무 프로필을 조회하고 예산 건강도를 분석해주세요.",
            "35세, moderate 위험성향, 1000만원 투자금액으로 투자 조언을 해주세요.",
            "연소득 6000만원에 신용카드 100만원, 의료비 50만원 공제 시 세금 최적화를 계산해주세요.",
            "KOSPI와 S&P 500 시장 인사이트를 제공해주세요."
        ]
        
        cols = st.columns(2)
        for i, query in enumerate(tool_queries):
            if cols[i % 2].button(query, key=f"tool_agent_{i}"):
                st.session_state.tool_agent_query = query
        
        # Tool Agent 인터페이스
        tool_query = st.text_input("질의를 입력하세요:", key="tool_agent_input")
        
        if st.button("🛠️ Tool Agent 실행", type="primary", disabled=st.session_state.is_loading) or st.session_state.get('tool_agent_query'):
            if tool_query or st.session_state.get('tool_agent_query'):
                query = tool_query or st.session_state.get('tool_agent_query')
                
                with st.spinner("Tool Agent 실행 중..."):
                    response = call_langgraph_api("/tool-agent", {
                        "query": query
                    })
                
                if response:
                    st.success("✅ Tool Agent 완료!")
                    
                    col1, col2 = st.columns([2, 1])
                    with col1:
                        st.subheader("🤖 AI 응답")
                        st.write(response["response"])
                    
                    with col2:
                        st.subheader("📋 실행 정보")
                        st.write(f"**방법**: {response['method']}")
                        st.write(f"**시간**: {response['timestamp']}")
                
                st.session_state.tool_agent_query = None
    
    # 탭 3: Multi Agent
    with tab3:
        st.header("🤖 LangGraph Multi Agent")
        st.info("LangGraph 기반 Multi Agent 시스템")
        
        # 샘플 질문들
        multi_queries = [
            "35세, 연소득 6000만원인 사용자의 종합적인 재무 상담을 받고 싶습니다.",
            "예산 분석, 투자 조언, 세금 최적화를 모두 포함한 종합 상담을 해주세요.",
            "시장 분석과 함께 개인 재무 상황을 종합적으로 진단해주세요."
        ]
        
        cols = st.columns(2)
        for i, query in enumerate(multi_queries):
            if cols[i % 2].button(query, key=f"multi_agent_{i}"):
                st.session_state.multi_agent_query = query
        
        # Multi Agent 인터페이스
        multi_query = st.text_input("복잡한 질의를 입력하세요:", key="multi_agent_input")
        
        if st.button("🤖 Multi Agent 실행", type="primary", disabled=st.session_state.is_loading) or st.session_state.get('multi_agent_query'):
            if multi_query or st.session_state.get('multi_agent_query'):
                query = multi_query or st.session_state.get('multi_agent_query')
                
                with st.spinner("Multi Agent 실행 중..."):
                    response = call_langgraph_api("/multi-agent", {
                        "query": query,
                        "thread_id": st.session_state.current_thread_id
                    })
                
                if response:
                    st.success("✅ Multi Agent 완료!")
                    
                    col1, col2 = st.columns([2, 1])
                    with col1:
                        st.subheader("🤖 AI 응답")
                        st.write(response["response"])
                    
                    with col2:
                        st.subheader("📋 실행 정보")
                        st.write(f"**방법**: {response['method']}")
                        st.write(f"**스레드 ID**: {response.get('thread_id', 'N/A')}")
                        st.write(f"**시간**: {response['timestamp']}")
                
                st.session_state.multi_agent_query = None
    
    # 탭 4: 종합 분석
    with tab4:
        st.header("📊 종합 재무 분석")
        st.info("Multi Agent를 활용한 종합적인 재무 분석")
        
        analysis_user_id = st.text_input("분석할 사용자 ID:", value="12345")
        
        if st.button("📊 종합 분석 실행", type="primary", disabled=st.session_state.is_loading):
            with st.spinner("종합 재무 분석을 수행하고 있습니다..."):
                response = call_langgraph_api("/comprehensive-analysis", {
                    "user_id": analysis_user_id,
                    "thread_id": st.session_state.current_thread_id
                })
            
            if response:
                st.success("✅ 종합 분석 완료!")
                
                col1, col2 = st.columns([2, 1])
                with col1:
                    st.subheader("📊 분석 결과")
                    st.write(response["response"])
                
                with col2:
                    st.subheader("📋 분석 정보")
                    st.write(f"**사용자 ID**: {response['user_id']}")
                    st.write(f"**방법**: {response['method']}")
                    st.write(f"**스레드 ID**: {response.get('thread_id', 'N/A')}")
                    st.write(f"**시간**: {response['timestamp']}")
    
    # 탭 5: 대화형 상담
    with tab5:
        st.header("💭 대화형 상담")
        st.info("Memory 기능을 포함한 대화형 재무 상담")
        
        # 대화 히스토리 표시
        st.subheader("💬 대화 기록")
        for i, message in enumerate(st.session_state.langgraph_chat_history):
            if message["role"] == "user":
                st.chat_message("user").write(message["content"])
            else:
                st.chat_message("assistant").write(message["content"])
        
        # 새로운 메시지 입력
        new_message = st.chat_input("메시지를 입력하세요...")
        
        if new_message:
            # 사용자 메시지 추가
            st.session_state.langgraph_chat_history.append({
                "role": "user",
                "content": new_message
            })
            
            # AI 응답 생성
            with st.spinner("대화형 상담 중..."):
                response = call_langgraph_api("/interactive-consultation", {
                    "message": new_message,
                    "thread_id": st.session_state.current_thread_id
                })
            
            if response:
                # AI 응답 추가
                st.session_state.langgraph_chat_history.append({
                    "role": "assistant",
                    "content": response["response"]
                })
                
                # 페이지 새로고침
                st.rerun()
        
        # 대화 초기화
        if st.button("🗑️ 대화 초기화", disabled=st.session_state.is_loading):
            st.session_state.langgraph_chat_history = []
            st.rerun()
    
    # 탭 6: 전문가 상담
    with tab6:
        st.header("👨‍💼 전문가별 상담")
        st.info("특정 전문가와의 상담")
        
        # 전문가 선택
        expert_type = st.selectbox(
            "상담할 전문가 선택",
            [
                "budget_analyst",
                "investment_advisor", 
                "tax_consultant",
                "market_analyst"
            ],
            format_func=lambda x: {
                "budget_analyst": "💰 예산 분석 전문가",
                "investment_advisor": "📈 투자 자문 전문가",
                "tax_consultant": "🧾 세무 전문가",
                "market_analyst": "📊 시장 분석 전문가"
            }[x]
        )
        
        # 전문가별 질의 입력
        expert_query = st.text_area("전문가에게 할 질의를 입력하세요:")
        
        if st.button("👨‍💼 전문가 상담 실행", type="primary", disabled=st.session_state.is_loading):
            if expert_query:
                with st.spinner("전문가 상담 중..."):
                    response = call_langgraph_api("/expert-consultation", {
                        "expert_type": expert_type,
                        "query": expert_query,
                        "thread_id": st.session_state.current_thread_id
                    })
                
                if response:
                    st.success("✅ 전문가 상담 완료!")
                    
                    # 전문가별 상담 기록 저장
                    if expert_type not in st.session_state.expert_consultations:
                        st.session_state.expert_consultations[expert_type] = []
                    
                    st.session_state.expert_consultations[expert_type].append({
                        "query": expert_query,
                        "response": response["response"],
                        "timestamp": response["timestamp"]
                    })
                    
                    col1, col2 = st.columns([2, 1])
                    with col1:
                        st.subheader("👨‍💼 전문가 응답")
                        st.write(response["response"])
                    
                    with col2:
                        st.subheader("📋 상담 정보")
                        st.write(f"**전문가**: {expert_type}")
                        st.write(f"**방법**: {response['method']}")
                        st.write(f"**스레드 ID**: {response.get('thread_id', 'N/A')}")
                        st.write(f"**시간**: {response['timestamp']}")
        
        # 전문가별 상담 기록 표시
        if expert_type in st.session_state.expert_consultations:
            st.subheader("📝 상담 기록")
            for i, consultation in enumerate(st.session_state.expert_consultations[expert_type]):
                with st.expander(f"상담 {i+1} - {consultation['timestamp']}"):
                    st.write(f"**질의**: {consultation['query']}")
                    st.write(f"**응답**: {consultation['response']}")
    
    # 탭 7: 시각화
    with tab7:
        st.header("📈 LangGraph 시각화")
        st.info("LangGraph 기능들의 시각적 표현")
        
        # 시각화 옵션
        viz_option = st.selectbox(
            "시각화 옵션",
            ["LangGraph 구조", "전문가 분포", "도구 사용 현황", "스레드 활동"]
        )
        
        if viz_option == "LangGraph 구조":
            st.subheader("🔄 LangGraph 구조도")
            
            # LangGraph 구조 시각화
            fig = go.Figure()
            
            # 노드 추가
            nodes = ["START", "Basic Chat", "Tool Agent", "Multi Agent", "Supervisor", "Budget Analyst", "Investment Advisor", "Tax Consultant", "Market Analyst", "END"]
            x_pos = [0, 2, 4, 6, 8, 6, 8, 10, 12, 14]
            y_pos = [0, 0, 0, 0, 0, -2, -1, 0, 1, 0]
            
            fig.add_trace(go.Scatter(
                x=x_pos, y=y_pos,
                mode='markers+text',
                marker=dict(size=20, color='lightblue'),
                text=nodes,
                textposition="middle center",
                name="노드"
            ))
            
            # 엣지 추가
            edges = [
                (0, 1), (1, 9),  # Basic Chat
                (0, 2), (2, 9),  # Tool Agent
                (0, 3), (3, 4),  # Multi Agent
                (4, 5), (5, 4),  # Budget Analyst
                (4, 6), (6, 4),  # Investment Advisor
                (4, 7), (7, 4),  # Tax Consultant
                (4, 8), (8, 4),  # Market Analyst
                (4, 9)  # END
            ]
            
            for start, end in edges:
                fig.add_trace(go.Scatter(
                    x=[x_pos[start], x_pos[end]],
                    y=[y_pos[start], y_pos[end]],
                    mode='lines',
                    line=dict(color='gray', width=2),
                    showlegend=False
                ))
            
            fig.update_layout(
                title="LangGraph 구조도",
                xaxis=dict(showgrid=False, showticklabels=False),
                yaxis=dict(showgrid=False, showticklabels=False),
                height=500
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        elif viz_option == "전문가 분포":
            st.subheader("👨‍💼 전문가 분포")
            
            # 전문가별 상담 횟수
            expert_counts = {}
            for expert_type, consultations in st.session_state.expert_consultations.items():
                expert_counts[expert_type] = len(consultations)
            
            if expert_counts:
                fig = px.pie(
                    values=list(expert_counts.values()),
                    names=list(expert_counts.keys()),
                    title="전문가별 상담 분포"
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("아직 전문가 상담 기록이 없습니다.")
        
        elif viz_option == "도구 사용 현황":
            st.subheader("🛠️ 도구 사용 현황")
            
            # 도구별 사용 현황 (모의 데이터)
            tools_data = {
                "get_user_financial_profile": 15,
                "analyze_budget_health": 12,
                "get_investment_advice": 8,
                "calculate_tax_optimization": 6,
                "get_market_insights": 10
            }
            
            fig = px.bar(
                x=list(tools_data.keys()),
                y=list(tools_data.values()),
                title="도구별 사용 횟수",
                labels={"x": "도구", "y": "사용 횟수"}
            )
            st.plotly_chart(fig, use_container_width=True)
        
        elif viz_option == "스레드 활동":
            st.subheader("📝 스레드 활동")
            
            # 스레드별 메시지 수 (모의 데이터)
            threads_data = {
                "user_12345": 5,
                "user_67890": 3,
                "user_abc123": 7,
                "user_def456": 2
            }
            
            fig = px.bar(
                x=list(threads_data.keys()),
                y=list(threads_data.values()),
                title="스레드별 메시지 수",
                labels={"x": "스레드 ID", "y": "메시지 수"}
            )
            st.plotly_chart(fig, use_container_width=True)

if __name__ == "__main__":
    main()
