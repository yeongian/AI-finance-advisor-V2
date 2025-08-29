#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
향상된 Streamlit UI
LangChain Expression Language를 사용한 고급 채팅 기능
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
    page_title="AI 재무관리 어드바이저 (향상된 기능)",
    page_icon="🚀",
    layout="wide"
)

# API 설정
API_BASE_URL = "http://localhost:8000"

# 세션 상태 초기화
if 'enhanced_chat_history' not in st.session_state:
    st.session_state.enhanced_chat_history = []
if 'user_data' not in st.session_state:
    st.session_state.user_data = {}

def call_enhanced_api(endpoint, data=None):
    """향상된 API 호출"""
    try:
        if data:
            response = requests.post(f"{API_BASE_URL}/enhanced{endpoint}", json=data, timeout=30)
        else:
            response = requests.get(f"{API_BASE_URL}/enhanced{endpoint}", timeout=30)
        
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
    st.title("🚀 AI 재무관리 어드바이저 (향상된 기능)")
    st.markdown("---")
    
    # 사이드바 - 사용자 정보 입력
    with st.sidebar:
        st.header("👤 사용자 정보")
        
        # 기본 정보 입력
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
            "age": age,
            "income": income,
            "expenses": expenses,
            "savings": savings,
            "risk_tolerance": risk_tolerance
        }
        
        st.markdown("---")
        
        # 향상된 기능 상태 확인
        if st.button("🔍 향상된 기능 상태 확인"):
            status = call_enhanced_api("/status")
            if status:
                st.success("✅ 향상된 기능 정상 작동")
                st.json(status)
            else:
                st.error("❌ 향상된 기능 연결 실패")
    
    # 메인 탭
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "💬 LCEL 채팅", 
        "📊 구조화된 분석", 
        "🔍 JSON 파서", 
        "🔄 대화 히스토리", 
        "🖼️ 멀티모달"
    ])
    
    # 탭 1: LCEL 체인 기반 채팅
    with tab1:
        st.header("💬 LCEL 체인 기반 채팅")
        st.info("LangChain Expression Language를 사용한 고급 채팅 기능")
        
        # 샘플 질문들
        sample_queries = [
            "월급 500만원일 때 예산 관리는 어떻게 해야 할까요?",
            "30대 초반의 투자 포트폴리오를 추천해주세요",
            "은퇴 준비를 위한 저축 계획을 세워주세요",
            "주택 구매를 위한 자금 계획을 도와주세요"
        ]
        
        cols = st.columns(2)
        for i, query in enumerate(sample_queries):
            if cols[i % 2].button(query, key=f"lcel_sample_{i}"):
                st.session_state.lcel_query = query
        
        # LCEL 채팅 인터페이스
        lcel_query = st.text_input("질문을 입력하세요:", key="lcel_input")
        
        if st.button("🚀 LCEL 체인으로 분석", type="primary") or st.session_state.get('lcel_query'):
            if lcel_query or st.session_state.get('lcel_query'):
                query = lcel_query or st.session_state.get('lcel_query')
                
                with st.spinner("LCEL 체인으로 분석 중..."):
                    response = call_enhanced_api("/lcel-query", {
                        "query": query,
                        "user_data": st.session_state.user_data
                    })
                
                if response:
                    st.success("✅ LCEL 체인 분석 완료!")
                    
                    col1, col2 = st.columns([2, 1])
                    with col1:
                        st.subheader("🤖 AI 응답")
                        st.write(response["response"])
                    
                    with col2:
                        st.subheader("📋 분석 정보")
                        st.write(f"**방법**: {response['method']}")
                        st.write(f"**시간**: {response['timestamp']}")
                        
                        # 사용량 정보 표시
                        if "usage" in response:
                            st.write("**토큰 사용량**:")
                            st.write(f"- 프롬프트: {response['usage'].get('prompt_tokens', 'N/A')}")
                            st.write(f"- 완료: {response['usage'].get('completion_tokens', 'N/A')}")
                            st.write(f"- 총합: {response['usage'].get('total_tokens', 'N/A')}")
                
                st.session_state.lcel_query = None
    
    # 탭 2: 구조화된 분석
    with tab2:
        st.header("📊 구조화된 분석")
        st.info("Pydantic 모델을 사용한 타입 안전한 구조화된 분석")
        
        analysis_type = st.selectbox(
            "분석 유형 선택",
            ["financial", "budget", "investment"],
            format_func=lambda x: {
                "financial": "재무 상황 분석",
                "budget": "예산 분석", 
                "investment": "투자 권장사항"
            }[x]
        )
        
        if st.button("🔍 구조화된 분석 실행", type="primary"):
            with st.spinner("구조화된 분석을 수행하고 있습니다..."):
                response = call_enhanced_api("/structured-analysis", {
                    "analysis_type": analysis_type,
                    "user_data": st.session_state.user_data
                })
            
            if response:
                st.success("✅ 구조화된 분석 완료!")
                
                result = response["result"]
                
                if analysis_type == "financial":
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.subheader("📈 분석 요약")
                        st.write(result["summary"])
                        
                        st.subheader("⚠️ 위험도")
                        risk_color = {
                            "low": "🟢",
                            "moderate": "🟡", 
                            "high": "🔴"
                        }.get(result["risk_level"], "⚪")
                        st.write(f"{risk_color} {result['risk_level']}")
                        
                        st.subheader("🎯 신뢰도")
                        confidence = result["confidence_score"]
                        st.progress(confidence)
                        st.write(f"{confidence:.1%}")
                    
                    with col2:
                        st.subheader("💡 권장사항")
                        for i, rec in enumerate(result["recommendations"], 1):
                            st.write(f"{i}. {rec}")
                
                elif analysis_type == "budget":
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.subheader("💰 예산 현황")
                        st.metric("총 수입", format_currency(result["total_income"]))
                        st.metric("총 지출", format_currency(result["total_expenses"]))
                        st.metric("저축률", format_percentage(result["savings_rate"]))
                    
                    with col2:
                        st.subheader("📊 지출 카테고리")
                        if result["expense_categories"]:
                            fig = px.pie(
                                values=list(result["expense_categories"].values()),
                                names=list(result["expense_categories"].keys()),
                                title="지출 분포"
                            )
                            st.plotly_chart(fig, use_container_width=True)
                    
                    st.subheader("💡 개선 권장사항")
                    for i, rec in enumerate(result["recommendations"], 1):
                        st.write(f"{i}. {rec}")
                
                elif analysis_type == "investment":
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.subheader("📈 투자 권장사항")
                        st.metric("자산 유형", result["asset_type"])
                        st.metric("배분 비율", format_percentage(result["allocation_percentage"]))
                        st.metric("예상 수익률", format_percentage(result["expected_return"]))
                        
                        st.subheader("⚠️ 위험도")
                        st.write(result["risk_level"])
                    
                    with col2:
                        st.subheader("💭 권장 이유")
                        st.write(result["reasoning"])
    
    # 탭 3: JSON 파서 테스트
    with tab3:
        st.header("🔍 JSON 파서 테스트")
        st.info("JSON 출력 파서를 사용한 구조화된 응답")
        
        json_query = st.text_area(
            "분석할 내용을 입력하세요:",
            placeholder="예: 30대 직장인의 재무 상황을 분석해주세요.",
            height=100
        )
        
        if st.button("🔍 JSON 파서로 분석", type="primary"):
            if json_query:
                with st.spinner("JSON 파서로 분석 중..."):
                    response = call_enhanced_api("/json-parser", {
                        "query": json_query,
                        "user_data": st.session_state.user_data
                    })
                
                if response:
                    st.success("✅ JSON 파서 분석 완료!")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.subheader("📋 분석 결과")
                        st.json(response["result"])
                    
                    with col2:
                        st.subheader("📊 분석 정보")
                        st.write(f"**방법**: {response['method']}")
                        st.write(f"**시간**: {response['timestamp']}")
    
    # 탭 4: 대화 히스토리 기반 채팅
    with tab4:
        st.header("🔄 대화 히스토리 기반 채팅")
        st.info("이전 대화 내용을 기억하는 고급 채팅 기능")
        
        # 대화 히스토리 표시
        st.subheader("💬 대화 기록")
        for i, message in enumerate(st.session_state.enhanced_chat_history):
            if message["role"] == "user":
                st.chat_message("user").write(message["content"])
            else:
                st.chat_message("assistant").write(message["content"])
        
        # 새로운 메시지 입력
        new_message = st.chat_input("메시지를 입력하세요...")
        
        if new_message:
            # 사용자 메시지 추가
            st.session_state.enhanced_chat_history.append({
                "role": "user",
                "content": new_message
            })
            
            # AI 응답 생성
            with st.spinner("대화 히스토리를 고려한 응답 생성 중..."):
                response = call_enhanced_api("/chat-with-history", {
                    "message": new_message,
                    "chat_history": st.session_state.enhanced_chat_history[:-1],  # 현재 메시지 제외
                    "user_data": st.session_state.user_data
                })
            
            if response:
                # AI 응답 추가
                st.session_state.enhanced_chat_history.append({
                    "role": "assistant",
                    "content": response["response"]
                })
                
                # 페이지 새로고침
                st.rerun()
        
        # 대화 초기화
        if st.button("🗑️ 대화 초기화"):
            st.session_state.enhanced_chat_history = []
            st.rerun()
    
    # 탭 5: 멀티모달 분석
    with tab5:
        st.header("🖼️ 멀티모달 분석")
        st.info("텍스트와 이미지를 함께 분석하는 고급 기능")
        
        multimodal_text = st.text_area(
            "분석할 텍스트를 입력하세요:",
            placeholder="예: 이 차트를 분석해주세요.",
            height=100
        )
        
        image_url = st.text_input(
            "이미지 URL (선택사항):",
            placeholder="https://example.com/image.jpg"
        )
        
        if st.button("🔍 멀티모달 분석", type="primary"):
            if multimodal_text:
                with st.spinner("멀티모달 분석 중..."):
                    response = call_enhanced_api("/multimodal-analysis", {
                        "text": multimodal_text,
                        "image_url": image_url if image_url else None,
                        "user_data": st.session_state.user_data
                    })
                
                if response:
                    st.success("✅ 멀티모달 분석 완료!")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.subheader("🤖 분석 결과")
                        st.write(response["response"])
                    
                    with col2:
                        st.subheader("📊 분석 정보")
                        st.write(f"**텍스트**: {response['text']}")
                        if response['image_url']:
                            st.write(f"**이미지**: {response['image_url']}")
                        st.write(f"**방법**: {response['method']}")
                        st.write(f"**시간**: {response['timestamp']}")
            else:
                st.warning("분석할 텍스트를 입력해주세요.")

if __name__ == "__main__":
    main()
