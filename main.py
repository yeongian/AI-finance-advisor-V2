#!/usr/bin/env python3
"""
AI 개인 재무 관리 어드바이저 - 메인 애플리케이션
AI 부트캠프 과제를 위한 완성된 웹 인터페이스
"""

import streamlit as st
import requests
import json
import logging
from datetime import datetime
import time
import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# 환경 변수 로딩
load_dotenv()

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/streamlit_app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 페이지 설정 - 성능 최적화
st.set_page_config(
    page_title="AI 재무관리 어드바이저",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="collapsed"  # 사이드바 접기로 초기 로딩 속도 향상
)

# API 설정
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
API_TIMEOUT = int(os.getenv("API_TIMEOUT", "30"))
CACHE_TTL = int(os.getenv("CACHE_TTL", "300"))

# 통합 API 호출 함수
def make_api_request(method: str, endpoint: str, data: dict = None, timeout: int = None) -> dict:
    """통합 API 호출 함수 (에러 처리 및 로깅 포함)"""
    if timeout is None:
        timeout = API_TIMEOUT
    
    url = f"{API_BASE_URL}{endpoint}"
    
    try:
        logger.info(f"API 요청: {method} {url}")
        start_time = time.time()
        
        if method.upper() == "GET":
            response = requests.get(url, timeout=timeout)
        elif method.upper() == "POST":
            response = requests.post(url, json=data, timeout=timeout)
        else:
            raise ValueError(f"지원하지 않는 HTTP 메서드: {method}")
        
        elapsed_time = time.time() - start_time
        logger.info(f"API 응답: {response.status_code} ({elapsed_time:.2f}초)")
        
        if response.status_code == 200:
            return response.json()
        else:
            logger.error(f"API 오류: {response.status_code} - {response.text}")
            return None
            
    except requests.exceptions.Timeout:
        logger.error(f"API 타임아웃: {url}")
        return None
    except requests.exceptions.ConnectionError:
        logger.error(f"API 연결 오류: {url}")
        return None
    except Exception as e:
        logger.error(f"API 요청 실패: {e}")
        return None

# 캐싱 설정
@st.cache_data(ttl=CACHE_TTL)
def check_api_health():
    """API 서버 상태 확인 (캐싱 적용)"""
    return make_api_request("GET", "/health", timeout=5) is not None

@st.cache_data(ttl=60)  # 1분 캐시
def call_api(endpoint, data=None):
    """API 호출 (캐싱 적용)"""
    if data:
        return make_api_request("POST", endpoint, data)
    else:
        return make_api_request("GET", endpoint)

def format_currency(amount):
    """통화 포맷팅"""
    return f"₩{amount:,.0f}"

def set_sample_question(question):
    """샘플 질문을 텍스트 입력란에 설정"""
    st.session_state.user_query = question

# 세션 상태 초기화 (한 번만 실행)
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'user_query' not in st.session_state:
    st.session_state.user_query = ""
if 'api_checked' not in st.session_state:
    st.session_state.api_checked = False
if 'app_start_time' not in st.session_state:
    st.session_state.app_start_time = time.time()

def render_project_info_tab():
    """프로젝트 정보 탭"""
    st.header("📋 프로젝트 정보")
    
    st.subheader("💰 AI 개인 재무 관리 어드바이저")
    st.write("AI 부트캠프 과제를 위한 완성된 AI Agent 시스템")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🎯 주요 기능")
        st.write("""
        1. 💰 예산 분석 및 추천
        2. 📈 투자 포트폴리오 최적화
        3. 📋 세금 절약 전략
        4. 🏠 부동산 투자 분석
        5. 🎯 은퇴 계획 수립
        """)
        
        st.subheader("🏗️ 기술 스택")
        st.write("""
        - LangChain & LangGraph: AI Agent 프레임워크
        - OpenAI GPT: 자연어 처리
        - RAG: 지식 검색 및 증강
        - Streamlit: 웹 인터페이스
        - FastAPI: 백엔드 API
        """)
    
    with col2:
        st.subheader("📊 평가 기준 충족")
        st.write("""
        ✅ Prompt Engineering: 최적화된 프롬프트 설계
        ✅ LangChain & LangGraph: 멀티 에이전트 구현
        ✅ RAG: 지식 검색 및 증강 시스템
        ✅ Streamlit: 사용자 인터페이스
        ✅ FastAPI: 백엔드 API
        ✅ Docker: 배포 환경
        """)
        
        st.subheader("💼 비즈니스 가치")
        st.write("""
        💡 실용성: 실제 재무 관리에 활용 가능
        💡 확장성: 다양한 금융 서비스로 확장 가능
        💡 차별화: 기존 서비스와 차별화된 기능
        """)
    
    st.subheader("📁 프로젝트 구조")
    st.code("""
AI-finance-advisor/
├── main.py                 # 메인 실행 파일 (현재 파일)
├── requirements.txt        # 의존성 패키지 목록
├── env_example.txt        # 환경변수 예제
├── README.md              # 프로젝트 설명서
├── src/                   # 소스 코드
│   ├── agents/           # AI 에이전트들
│   ├── core/             # 핵심 기능
│   ├── rag/              # RAG 시스템
│   └── api/              # API 서버
├── data/                 # 데이터 파일
└── logs/                 # 로그 파일
    """)
    
    st.subheader("🚀 시작하기")
    st.write("""
    1. 환경변수 설정: `env_example.txt` 참고
    2. 의존성 설치: `pip install -r requirements.txt`
    3. API 서버 실행: `py -m uvicorn src.api.main:app --host localhost --port 8000`
    4. 웹 앱 실행: `py -m streamlit run main.py --server.port 8501`
    """)

def render_ai_consultation_tab():
    """AI 상담 탭"""
    st.header("💬 AI 상담")
    
    # 샘플 질문 버튼들
    st.subheader("📝 샘플 질문")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("💰 예산 관리 방법", use_container_width=True):
            set_sample_question("월급의 30%를 저축하려고 하는데, 어떤 방법으로 예산을 관리하면 좋을까요?")
            st.rerun()
        
        if st.button("📈 투자 포트폴리오", use_container_width=True):
            set_sample_question("초보 투자자로서 안전하면서도 수익을 낼 수 있는 포트폴리오를 추천해주세요.")
            st.rerun()
    
    with col2:
        if st.button("🧾 세금 절약 전략", use_container_width=True):
            set_sample_question("연말정산에서 세금을 절약할 수 있는 방법들을 알려주세요.")
            st.rerun()
        
        if st.button("🎯 은퇴 계획", use_container_width=True):
            set_sample_question("30대 후반인데 은퇴를 위해 얼마나 저축해야 하고 어떤 준비를 해야 할까요?")
            st.rerun()
    
    with col3:
        if st.button("🏠 부동산 투자", use_container_width=True):
            set_sample_question("부동산 투자를 고려하고 있는데, 현재 시점에서 어떤 지역이나 유형이 좋을까요?")
            st.rerun()
        
        if st.button("💳 신용카드 관리", use_container_width=True):
            set_sample_question("신용카드를 효율적으로 사용하면서 신용점수를 관리하는 방법을 알려주세요.")
            st.rerun()
    
    # 사용자 입력
    st.subheader("💭 질문하기")
    user_query = st.text_area(
        "재무 관련 질문을 입력하세요:",
        value=st.session_state.user_query,
        height=100,
        placeholder="예: 월급의 30%를 저축하려고 하는데, 어떤 방법으로 예산을 관리하면 좋을까요?"
    )
    
    if st.button("🤖 AI에게 질문하기", type="primary"):
        if user_query.strip():
            start_time = time.time()
            
            with st.spinner("AI가 답변을 생성하고 있습니다..."):
                # API 호출
                response = call_api("/query", {"query": user_query})
            
            elapsed_time = time.time() - start_time
            
            if response and "answer" in response:
                # 채팅 히스토리에 추가
                st.session_state.chat_history.append({
                    "user": user_query,
                    "ai": response["answer"],
                    "timestamp": datetime.now().strftime("%H:%M"),
                    "agent_type": response.get("agent_type", "unknown")
                })
                
                # 답변 표시
                st.success(f"✅ 답변 완료! (소요시간: {elapsed_time:.2f}초)")
                st.write(response["answer"])
                
                # 에이전트 정보 표시
                if "agent_type" in response:
                    agent_names = {
                        "budget": "💰 예산 관리",
                        "investment": "📈 투자 관리",
                        "tax": "🧾 세금 관리",
                        "retirement": "🎯 은퇴 계획",
                        "comprehensive": "🤖 종합 분석"
                    }
                    agent_name = agent_names.get(response["agent_type"], "AI 어드바이저")
                    st.info(f"답변 제공: {agent_name}")
                
                # 컨텍스트 사용 여부
                if response.get("context_used"):
                    st.info("📚 지식베이스의 관련 정보를 참조했습니다.")
                
            else:
                st.error("❌ 답변을 생성할 수 없습니다. API 서버를 확인해주세요.")
            
            # 입력 필드 초기화
            st.session_state.user_query = ""
            st.rerun()
        else:
            st.warning("⚠️ 질문을 입력해주세요.")
    
    # 채팅 히스토리
    if st.session_state.chat_history:
        st.subheader("💬 대화 기록")
        
        # 최신 대화부터 표시
        for i, chat in enumerate(reversed(st.session_state.chat_history[-10:])):  # 최근 10개만 표시
            with st.expander(f"💬 {chat['timestamp']} - {chat['user'][:50]}..."):
                st.write(f"**사용자:** {chat['user']}")
                st.write(f"**AI:** {chat['ai']}")
                if 'agent_type' in chat:
                    agent_names = {
                        "budget": "💰 예산 관리",
                        "investment": "📈 투자 관리",
                        "tax": "🧾 세금 관리",
                        "retirement": "🎯 은퇴 계획",
                        "comprehensive": "🤖 종합 분석"
                    }
                    agent_name = agent_names.get(chat["agent_type"], "AI 어드바이저")
                    st.caption(f"답변 제공: {agent_name}")

def render_comprehensive_analysis_tab():
    """종합 분석 탭"""
    st.header("📊 종합 분석")
    
    st.info("💡 이 기능은 사용자의 재무 정보를 종합적으로 분석하여 맞춤형 조언을 제공합니다.")
    
    with st.form("comprehensive_analysis"):
        st.subheader("📋 기본 정보")
        
        col1, col2 = st.columns(2)
        
        with col1:
            age = st.number_input("나이", min_value=18, max_value=100, value=30)
            income = st.number_input("연소득 (원)", min_value=0, value=50000000, step=1000000)
            expenses = st.number_input("연지출 (원)", min_value=0, value=30000000, step=1000000)
        
        with col2:
            savings = st.number_input("현재 저축액 (원)", min_value=0, value=10000000, step=1000000)
            risk_tolerance = st.selectbox(
                "위험 성향",
                ["conservative", "moderate", "aggressive"],
                format_func=lambda x: {"conservative": "보수적", "moderate": "중립적", "aggressive": "공격적"}[x]
            )
        
        st.subheader("💰 월별 지출 세부사항")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            housing = st.number_input("주거비 (월)", min_value=0, value=800000, step=10000)
            food = st.number_input("식비 (월)", min_value=0, value=500000, step=10000)
        
        with col2:
            transportation = st.number_input("교통비 (월)", min_value=0, value=300000, step=10000)
            utilities = st.number_input("공과금 (월)", min_value=0, value=200000, step=10000)
        
        with col3:
            entertainment = st.number_input("여가비 (월)", min_value=0, value=200000, step=10000)
            other = st.number_input("기타 (월)", min_value=0, value=100000, step=10000)
        
        st.subheader("📈 현재 투자 현황")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            stocks = st.number_input("주식 투자 (원)", min_value=0, value=5000000, step=100000)
        
        with col2:
            bonds = st.number_input("채권 투자 (원)", min_value=0, value=2000000, step=100000)
        
        with col3:
            cash = st.number_input("현금 보유 (원)", min_value=0, value=3000000, step=100000)
        
        submitted = st.form_submit_button("📊 종합 분석 실행", type="primary")
        
        if submitted:
            # 사용자 데이터 구성
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
            
            # 분석 요청
            start_time = time.time()
            
            with st.spinner("종합 분석을 수행하고 있습니다..."):
                response = call_api("/comprehensive-analysis", {"user_data": user_data})
            
            elapsed_time = time.time() - start_time
            
            if response and "analysis" in response:
                st.success(f"✅ 분석 완료! (소요시간: {elapsed_time:.2f}초)")
                
                # 분석 결과 표시
                analysis = response["analysis"]
                
                # 예산 분석
                if "budget_analysis" in analysis:
                    st.subheader("💰 예산 분석")
                    st.write(analysis["budget_analysis"])
                
                # 투자 분석
                if "investment_analysis" in analysis:
                    st.subheader("📈 투자 분석")
                    st.write(analysis["investment_analysis"])
                
                # 세금 분석
                if "tax_analysis" in analysis:
                    st.subheader("🧾 세금 분석")
                    st.write(analysis["tax_analysis"])
                
                # 은퇴 분석
                if "retirement_analysis" in analysis:
                    st.subheader("🎯 은퇴 계획 분석")
                    st.write(analysis["retirement_analysis"])
                
                # 종합 권장사항
                if "recommendations" in analysis:
                    st.subheader("💡 종합 권장사항")
                    st.write(analysis["recommendations"])
                
            else:
                st.error("❌ 분석을 수행할 수 없습니다. API 서버를 확인해주세요.")

def main():
    """메인 함수"""
    # 헤더 최적화
    st.title("💰 AI 재무관리 어드바이저")
    
    # API 상태 확인 (캐싱 활용)
    if not st.session_state.api_checked:
        with st.spinner("API 서버 연결 확인 중..."):
            api_healthy = check_api_health()
            st.session_state.api_checked = True
            st.session_state.api_healthy = api_healthy
    else:
        api_healthy = st.session_state.api_healthy
    
    if not api_healthy:
        st.error("⚠️ API 서버에 연결할 수 없습니다. API 서버가 실행 중인지 확인해주세요.")
        st.info("API 서버 실행: `py -m uvicorn src.api.main:app --host localhost --port 8000`")
        
        # API 서버가 없어도 프로젝트 정보는 볼 수 있도록
        st.warning("API 서버가 실행되지 않아 일부 기능을 사용할 수 없습니다.")
        render_project_info_tab()
        return
    
    st.success("✅ API 서버에 연결되었습니다!")
    
    # 탭 생성 (지연 로딩)
    tab_names = ["📋 프로젝트 정보", "💬 AI 상담", "📊 종합 분석", "💰 예산 관리", "📈 투자 관리", "🧾 세금 관리"]
    tabs = st.tabs(tab_names)
    
    # 프로젝트 정보 탭
    with tabs[0]:
        render_project_info_tab()
    
    # AI 상담 탭
    with tabs[1]:
        render_ai_consultation_tab()
    
    # 종합 분석 탭
    with tabs[2]:
        render_comprehensive_analysis_tab()
    
    # 나머지 탭들 (간단한 안내)
    with tabs[3]:
        st.header("💰 예산 관리")
        st.info("💡 이 기능은 예산 분석 및 추천을 제공합니다.")
        st.write("AI 상담 탭에서 '예산 관리' 관련 질문을 해보세요!")
    
    with tabs[4]:
        st.header("📈 투자 관리")
        st.info("💡 이 기능은 투자 포트폴리오 최적화를 제공합니다.")
        st.write("AI 상담 탭에서 '투자' 관련 질문을 해보세요!")
    
    with tabs[5]:
        st.header("🧾 세금 관리")
        st.info("💡 이 기능은 세금 절약 전략을 제공합니다.")
        st.write("AI 상담 탭에서 '세금' 관련 질문을 해보세요!")

if __name__ == "__main__":
    main()
