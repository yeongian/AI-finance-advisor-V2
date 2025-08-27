"""
AI 개인 재무 관리 어드바이저 - Streamlit 웹 애플리케이션
"""

import streamlit as st
import sys
import os
import json
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

# 프로젝트 루트 경로 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from src.agents.budget_agent import BudgetAgent
from src.core.config import config
from src.core.utils import (
    setup_logging, 
    format_currency, 
    calculate_basic_metrics, 
    create_sample_data,
    get_financial_advice_category,
    format_financial_advice
)

# 페이지 설정
st.set_page_config(
    page_title="AI 개인 재무 관리 어드바이저",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 로깅 설정
logger = setup_logging()

def main():
    """메인 애플리케이션"""
    
    # 사이드바 설정
    setup_sidebar()
    
    # 메인 타이틀
    st.title("💰 AI 개인 재무 관리 어드바이저")
    st.markdown("---")
    
    # 탭 생성
    tab1, tab2, tab3, tab4 = st.tabs([
        "🏠 대시보드", 
        "💬 AI 상담", 
        "📊 재무 분석", 
        "⚙️ 설정"
    ])
    
    with tab1:
        show_dashboard()
    
    with tab2:
        show_ai_consultation()
    
    with tab3:
        show_financial_analysis()
    
    with tab4:
        show_settings()

def setup_sidebar():
    """사이드바 설정"""
    st.sidebar.title("🔧 설정")
    
    # API 키 확인
    if not config.validate():
        st.sidebar.error("⚠️ API 키가 설정되지 않았습니다!")
        st.sidebar.info("설정 탭에서 API 키를 확인하세요.")
        return False
    
    # Azure OpenAI 사용 여부 표시
    if config.is_azure_openai():
        st.sidebar.success("✅ Azure OpenAI 연결됨")
        st.sidebar.info(f"모델: {config.DEFAULT_MODEL}")
    else:
        st.sidebar.warning("⚠️ 일반 OpenAI 사용")
    
    # 사용자 정보 입력
    st.sidebar.subheader("👤 사용자 정보")
    
    # 세션 상태 초기화
    if 'user_data' not in st.session_state:
        st.session_state.user_data = create_sample_data()
    
    # 사용자 정보 입력 폼
    with st.sidebar.form("user_info"):
        age = st.number_input("나이", min_value=18, max_value=100, value=st.session_state.user_data.get('age', 30))
        income = st.number_input("연소득 (원)", min_value=0, value=st.session_state.user_data.get('income', 50000000), step=1000000)
        expenses = st.number_input("연지출 (원)", min_value=0, value=st.session_state.user_data.get('expenses', 30000000), step=1000000)
        savings = st.number_input("저축금 (원)", min_value=0, value=st.session_state.user_data.get('savings', 100000000), step=1000000)
        
        if st.form_submit_button("정보 업데이트"):
            st.session_state.user_data.update({
                'age': age,
                'income': income,
                'expenses': expenses,
                'savings': savings
            })
            st.success("사용자 정보가 업데이트되었습니다!")
    
    # 재무 건강도 표시
    if st.session_state.user_data:
        metrics = calculate_basic_metrics(
            st.session_state.user_data['income'],
            st.session_state.user_data['expenses'],
            st.session_state.user_data['savings']
        )
        
        st.sidebar.subheader("📈 재무 건강도")
        
        # 건강도 점수 게이지
        health_score = metrics['financial_health_score']
        if health_score >= 80:
            st.sidebar.success(f"우수: {health_score:.0f}/100")
        elif health_score >= 60:
            st.sidebar.info(f"양호: {health_score:.0f}/100")
        elif health_score >= 40:
            st.sidebar.warning(f"보통: {health_score:.0f}/100")
        else:
            st.sidebar.error(f"개선 필요: {health_score:.0f}/100")
        
        st.sidebar.metric("저축률", f"{metrics['savings_rate']:.1f}%")
        st.sidebar.metric("비상금 개월", f"{metrics['emergency_fund_months']:.1f}개월")
    
    return True

def show_dashboard():
    """대시보드 탭"""
    st.header("📊 재무 대시보드")
    
    if 'user_data' not in st.session_state:
        st.warning("사용자 정보를 먼저 입력해주세요.")
        return
    
    user_data = st.session_state.user_data
    
    # 기본 재무 지표
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("연소득", format_currency(user_data['income']))
    
    with col2:
        st.metric("연지출", format_currency(user_data['expenses']))
    
    with col3:
        net_income = user_data['income'] - user_data['expenses']
        st.metric("순소득", format_currency(net_income))
    
    with col4:
        st.metric("저축금", format_currency(user_data['savings']))
    
    # 차트 섹션
    col1, col2 = st.columns(2)
    
    with col1:
        # 소득/지출 파이 차트
        st.subheader("💰 소득 vs 지출")
        fig_pie = go.Figure(data=[go.Pie(
            labels=['소득', '지출'],
            values=[user_data['income'], user_data['expenses']],
            hole=0.3
        )])
        fig_pie.update_layout(height=400)
        st.plotly_chart(fig_pie, use_container_width=True)
    
    with col2:
        # 월별 지출 바 차트
        if 'monthly_expenses' in user_data:
            st.subheader("📅 월별 지출 분석")
            expenses_data = user_data['monthly_expenses']
            df_expenses = pd.DataFrame(list(expenses_data.items()), columns=['카테고리', '금액'])
            
            fig_bar = px.bar(
                df_expenses, 
                x='카테고리', 
                y='금액',
                title="카테고리별 월 지출"
            )
            fig_bar.update_layout(height=400)
            st.plotly_chart(fig_bar, use_container_width=True)
    
    # 재무 목표 섹션
    if 'financial_goals' in user_data and user_data['financial_goals']:
        st.subheader("🎯 재무 목표")
        
        goals_df = pd.DataFrame(user_data['financial_goals'])
        for _, goal in goals_df.iterrows():
            with st.expander(f"🎯 {goal['goal']}"):
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("목표 금액", format_currency(goal['target_amount']))
                with col2:
                    st.metric("목표 기간", f"{goal['target_year']}년")
                with col3:
                    monthly_needed = goal['target_amount'] / (goal['target_year'] * 12)
                    st.metric("월 필요 금액", format_currency(monthly_needed))

def show_ai_consultation():
    """AI 상담 탭"""
    st.header("💬 AI 재무 상담")
    
    # API 키 확인
    if not config.validate():
        st.error("API 키가 설정되지 않았습니다. 설정 탭에서 API 키를 확인하세요.")
        return
    
    # AI Agent 초기화
    if 'budget_agent' not in st.session_state:
        st.session_state.budget_agent = BudgetAgent()
    
    # 상담 기록 초기화
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    
    # 사용자 입력
    user_query = st.text_area(
        "재무 관련 질문을 입력하세요:",
        placeholder="예: 월급을 어떻게 관리하면 좋을까요? 투자 포트폴리오를 어떻게 구성해야 할까요?",
        height=100
    )
    
    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button("💬 상담 시작", type="primary"):
            if user_query.strip():
                process_consultation(user_query)
    
    with col2:
        if st.button("🗑️ 대화 기록 삭제"):
            st.session_state.chat_history = []
            st.session_state.budget_agent.clear_memory()
            st.success("대화 기록이 삭제되었습니다.")
    
    # 상담 기록 표시
    if st.session_state.chat_history:
        st.subheader("📝 상담 기록")
        
        for i, (query, response, category) in enumerate(st.session_state.chat_history):
            with st.expander(f"질문 {i+1}: {query[:50]}..."):
                st.markdown(f"**질문:** {query}")
                st.markdown("---")
                st.markdown(format_financial_advice(response, category))

def process_consultation(user_query: str):
    """AI 상담 처리"""
    try:
        with st.spinner("AI가 분석 중입니다..."):
            # 카테고리 분류
            category = get_financial_advice_category(user_query)
            
            # AI Agent로 응답 생성
            user_data = st.session_state.get('user_data', {})
            response_data = st.session_state.budget_agent.process_query(user_query, user_data)
            
            response = response_data['response']
            
            # 대화 기록에 추가
            st.session_state.chat_history.append((user_query, response, category))
            
            # 성공 메시지
            st.success("상담이 완료되었습니다!")
            
    except Exception as e:
        st.error(f"상담 처리 중 오류가 발생했습니다: {str(e)}")
        logger.error(f"상담 처리 오류: {e}")

def show_financial_analysis():
    """재무 분석 탭"""
    st.header("📊 상세 재무 분석")
    
    if 'user_data' not in st.session_state:
        st.warning("사용자 정보를 먼저 입력해주세요.")
        return
    
    user_data = st.session_state.user_data
    
    # 재무 지표 계산
    metrics = calculate_basic_metrics(
        user_data['income'],
        user_data['expenses'],
        user_data['savings']
    )
    
    # 지표 카드들
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("저축률", f"{metrics['savings_rate']:.1f}%")
        if metrics['savings_rate'] >= 20:
            st.success("목표 저축률 달성!")
        elif metrics['savings_rate'] >= 10:
            st.info("저축률 개선 필요")
        else:
            st.warning("저축률 대폭 개선 필요")
    
    with col2:
        st.metric("비상금 보유 개월", f"{metrics['emergency_fund_months']:.1f}개월")
        if metrics['emergency_fund_months'] >= 6:
            st.success("충분한 비상금 보유")
        elif metrics['emergency_fund_months'] >= 3:
            st.info("비상금 추가 필요")
        else:
            st.warning("비상금 확보 시급")
    
    with col3:
        st.metric("재무 건강도", f"{metrics['financial_health_score']:.0f}/100")
        if metrics['financial_health_score'] >= 80:
            st.success("우수한 재무 상태")
        elif metrics['financial_health_score'] >= 60:
            st.info("양호한 재무 상태")
        else:
            st.warning("재무 상태 개선 필요")
    
    # 월별 지출 분석
    if 'monthly_expenses' in user_data:
        st.subheader("📅 월별 지출 상세 분석")
        
        expenses_data = user_data['monthly_expenses']
        total_monthly = sum(expenses_data.values())
        
        # 지출 비율 계산
        expense_analysis = []
        for category, amount in expenses_data.items():
            percentage = (amount / total_monthly) * 100
            expense_analysis.append({
                '카테고리': category,
                '금액': amount,
                '비율': percentage
            })
        
        df_analysis = pd.DataFrame(expense_analysis)
        
        # 지출 비율 차트
        fig_pie = px.pie(
            df_analysis, 
            values='금액', 
            names='카테고리',
            title="카테고리별 지출 비율"
        )
        st.plotly_chart(fig_pie, use_container_width=True)
        
        # 지출 상세 테이블
        st.dataframe(
            df_analysis.sort_values('금액', ascending=False),
            use_container_width=True
        )

def show_settings():
    """설정 탭"""
    st.header("⚙️ 설정")
    
    # API 설정 상태
    st.subheader("🔑 API 설정 상태")
    
    if config.is_azure_openai():
        st.success("✅ Azure OpenAI 연결됨")
        col1, col2 = st.columns(2)
        with col1:
            st.info(f"**엔드포인트:** {config.AOAI_ENDPOINT}")
            st.info(f"**API 키:** {config.AOAI_API_KEY[:10]}...")
        with col2:
            st.info(f"**모델:** {config.DEFAULT_MODEL}")
            st.info(f"**임베딩 모델:** {config.EMBEDDING_MODEL}")
    else:
        st.warning("⚠️ Azure OpenAI 설정이 필요합니다")
        st.info("env_example.txt를 .env로 복사하고 Azure OpenAI 설정을 입력하세요.")
    
    # 앱 정보
    st.subheader("ℹ️ 앱 정보")
    
    info_col1, info_col2 = st.columns(2)
    
    with info_col1:
        st.info(f"**버전:** 1.0.0")
        st.info(f"**Python:** {sys.version}")
    
    with info_col2:
        st.info(f"**모델:** {config.DEFAULT_MODEL}")
        st.info(f"**임베딩 모델:** {config.EMBEDDING_MODEL}")
    
    # 개발자 정보
    st.subheader("👨‍💻 개발자 정보")
    st.markdown("""
    - **프로젝트:** AI 개인 재무 관리 어드바이저
    - **기술 스택:** LangChain, Streamlit, Azure OpenAI
    - **목적:** 개인 재무 관리 최적화 지원
    """)
    
    # 환경변수 설정 가이드
    st.subheader("📝 환경변수 설정 가이드")
    st.markdown("""
    1. `env_example.txt` 파일을 `.env`로 복사
    2. Azure OpenAI 설정 입력:
       ```
       AOAI_ENDPOINT=https://your-endpoint.openai.azure.com/
       AOAI_API_KEY=your_api_key_here
       AOAI_DEPLOY_GPT4O_MINI=gpt-4o-mini
       ```
    3. 앱 재시작
    """)

if __name__ == "__main__":
    main()
