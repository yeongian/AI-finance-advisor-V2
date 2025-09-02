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

# 로깅 설정 (UTF-8 인코딩으로 설정)
import sys
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/streamlit_app.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# 페이지 설정 - 극한 성능 최적화
st.set_page_config(
    page_title="AI 재무관리 어드바이저",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="collapsed",  # 사이드바 접기로 초기 로딩 속도 향상
    menu_items=None  # 메뉴 비활성화로 로딩 속도 향상
)

# API 설정
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
API_TIMEOUT = int(os.getenv("API_TIMEOUT", "15"))  # 타임아웃 단축 (성능 개선)
CACHE_TTL = int(os.getenv("CACHE_TTL", "300"))

# API 연결 재시도 설정 (최적화)
API_RETRY_COUNT = 1  # 재시도 횟수 감소 (빠른 실패)
API_RETRY_DELAY = 0.5  # 재시도 간격 단축

# 통합 API 호출 함수 (재시도 로직 포함)
def make_api_request(method: str, endpoint: str, data: dict = None, timeout: int = None) -> dict:
    """통합 API 호출 함수 (에러 처리 및 로깅 포함)"""
    if timeout is None:
        timeout = API_TIMEOUT
    
    url = f"{API_BASE_URL}{endpoint}"
    
    for attempt in range(API_RETRY_COUNT):
        try:
            logger.info(f"API 요청 (시도 {attempt + 1}/{API_RETRY_COUNT}): {method} {url}")
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
            logger.error(f"API 타임아웃 (시도 {attempt + 1}): {url}")
            if attempt < API_RETRY_COUNT - 1:
                time.sleep(API_RETRY_DELAY)
                continue
            return {"error": f"API 타임아웃 (시도 {attempt + 1}): {timeout}초 초과"}
        except requests.exceptions.ConnectionError:
            logger.error(f"API 연결 오류 (시도 {attempt + 1}): {url}")
            if attempt < API_RETRY_COUNT - 1:
                time.sleep(API_RETRY_DELAY)
                continue
            return {"error": f"API 서버 연결 실패 (시도 {attempt + 1}): 서버가 실행되지 않았거나 네트워크 문제"}
        except Exception as e:
            logger.error(f"API 요청 실패 (시도 {attempt + 1}): {e}")
            if attempt < API_RETRY_COUNT - 1:
                time.sleep(API_RETRY_DELAY)
                continue
            return {"error": f"API 요청 실패 (시도 {attempt + 1}): {str(e)}"}
    
    return None

# 캐싱 설정 (최적화)
@st.cache_data(ttl=5)  # 5초 캐시로 단축 (더 자주 확인)
def check_api_health():
    """API 서버 상태 확인"""
    try:
        result = make_api_request("GET", "/health", timeout=3)  # 타임아웃 더 단축
        if result is None:
            return False
        # 응답 내용도 확인
        if isinstance(result, dict) and result.get("status") == "healthy":
            return True
        return False
    except Exception as e:
        logger.error(f"API 헬스 체크 실패: {e}")
        return False

@st.cache_data(ttl=10)  # 10초 캐시
def call_api(endpoint, data=None):
    """API 호출"""
    if data:
        return make_api_request("POST", endpoint, data)
    else:
        return make_api_request("GET", endpoint)

# 실시간 데이터 관련 함수들
def create_market_dashboard():
    """시장 대시보드 생성"""
    # 코스피/코스닥/환율 정보 제거 - 간단한 대시보드만 표시
    st.subheader("📈 AI 재무관리 어드바이저")
    st.info("💡 AI 기반 개인 재무 관리 및 투자 자문 시스템입니다.")

def create_portfolio_chart(portfolio_data):
    """포트폴리오 차트 생성"""
    if not PLOTLY_AVAILABLE:
        st.warning("plotly가 설치되지 않아 차트를 표시할 수 없습니다.")
        return None
        
    if not portfolio_data or "error" in portfolio_data:
        return None
    
    try:
        # 포트폴리오 성과 차트
        fig = go.Figure()
        
        # 수익률 라인 차트
        if "portfolio_returns" in portfolio_data:
            returns = portfolio_data["portfolio_returns"]
            dates = pd.date_range(start=portfolio_data.get("start_date", "2023-01-01"), 
                                periods=len(returns), freq='D')
            
            fig.add_trace(go.Scatter(
                x=dates,
                y=returns.cumsum() * 100,  # 누적 수익률을 퍼센트로
                mode='lines',
                name='포트폴리오 수익률',
                line=dict(color='#1f77b4', width=2)
            ))
        
        fig.update_layout(
            title="포트폴리오 성과 추이",
            xaxis_title="날짜",
            yaxis_title="누적 수익률 (%)",
            height=400,
            showlegend=True
        )
        
        return fig
    except Exception as e:
        logger.error(f"포트폴리오 차트 생성 실패: {e}")
        return None

def create_expense_pie_chart(expenses_data):
    """지출 파이 차트 생성"""
    if not PLOTLY_AVAILABLE:
        st.warning("plotly가 설치되지 않아 차트를 표시할 수 없습니다.")
        return None
        
    if not expenses_data:
        return None
    
    try:
        # 카테고리별 지출 데이터
        categories = list(expenses_data.keys())
        amounts = list(expenses_data.values())
        
        fig = px.pie(
            values=amounts,
            names=categories,
            title="월별 지출 분포",
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        
        fig.update_traces(textposition='inside', textinfo='percent+label')
        fig.update_layout(height=400)
        
        return fig
    except Exception as e:
        logger.error(f"지출 차트 생성 실패: {e}")
        return None

def format_currency(amount):
    """통화 포맷팅"""
    return f"₩{amount:,.0f}"

# 세션 상태 초기화 (한 번만 실행)
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'user_query' not in st.session_state:
    st.session_state.user_query = ""
if 'api_checked' not in st.session_state:
    st.session_state.api_checked = False
if 'app_start_time' not in st.session_state:
    st.session_state.app_start_time = time.time()
if 'auto_submit' not in st.session_state:
    st.session_state.auto_submit = False
if 'is_loading' not in st.session_state:
    st.session_state.is_loading = False
if 'analysis_type' not in st.session_state:
    st.session_state.analysis_type = None
if 'show_detailed' not in st.session_state:
    st.session_state.show_detailed = False
if 'show_summary' not in st.session_state:
    st.session_state.show_summary = False

if 'quick_analysis' not in st.session_state:
    st.session_state.quick_analysis = None
if 'show_question_input' not in st.session_state:
    st.session_state.show_question_input = False

def render_ai_consultation_tab():
    """AI 상담 탭"""
    st.header("💬 AI 상담")ㅅㅅ
    
    # 샘플 질문 버튼들
    st.subheader("📝 샘플 질문")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("💰 예산 관리 방법", use_container_width=True, disabled=st.session_state.is_loading):
            st.session_state.user_query = "월급의 30%를 저축하려고 하는데, 어떤 방법으로 예산을 관리하면 좋을까요?"
            st.session_state.ai_consultation_auto_submit = True
        
        if st.button("📈 투자 포트폴리오", use_container_width=True, disabled=st.session_state.is_loading):
            st.session_state.user_query = "초보 투자자로서 안전하면서도 수익을 낼 수 있는 포트폴리오를 추천해주세요."
            st.session_state.ai_consultation_auto_submit = True
    
    with col2:
        if st.button("🧾 세금 절약 전략", use_container_width=True, disabled=st.session_state.is_loading):
            st.session_state.user_query = "연말정산에서 세금을 절약할 수 있는 방법들을 알려주세요."
            st.session_state.ai_consultation_auto_submit = True
        
        if st.button("🎯 은퇴 계획", use_container_width=True, disabled=st.session_state.is_loading):
            st.session_state.user_query = "30대 후반인데 은퇴를 위해 얼마나 저축해야 하고 어떤 준비를 해야 할까요?"
            st.session_state.ai_consultation_auto_submit = True
    
    with col3:
        if st.button("🏠 부동산 투자", use_container_width=True, disabled=st.session_state.is_loading):
            st.session_state.user_query = "부동산 투자를 고려하고 있는데, 현재 시점에서 어떤 지역이나 유형이 좋을까요?"
            st.session_state.ai_consultation_auto_submit = True
        
        if st.button("💳 신용카드 관리", use_container_width=True, disabled=st.session_state.is_loading):
            st.session_state.user_query = "신용카드를 효율적으로 사용하면서 신용점수를 관리하는 방법을 알려주세요."
            st.session_state.ai_consultation_auto_submit = True
    
    # 샘플 질문 아래 간단한 질문하기 버튼
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("💭 질문하기", type="primary", use_container_width=True, disabled=st.session_state.is_loading):
            st.session_state.show_question_input = True
    
    # 사용자 입력 (조건부 표시)
    submit_button = False
    user_query = ""
    
    if st.session_state.get('show_question_input', False):
        user_query = st.text_area(
            "재무 관련 질문을 입력하세요:",
            value=st.session_state.user_query,
            height=100,
            placeholder="예: 월급의 30%를 저축하려고 하는데, 어떤 방법으로 예산을 관리하면 좋을까요?"
        )
        
        col1, col2 = st.columns([1, 4])
        with col1:
            submit_button = st.button("🤖 AI에게 질문하기", type="primary", disabled=st.session_state.is_loading)
        
        with col2:
            if st.button("🗑️ 입력 초기화", type="secondary", disabled=st.session_state.is_loading):
                st.session_state.user_query = ""
                st.session_state.show_question_input = False
    
    # 질문 처리
    if submit_button or st.session_state.get('ai_consultation_auto_submit', False):
        if user_query.strip():
            # 자동 제출 상태 초기화
            st.session_state.ai_consultation_auto_submit = False
            
            # 로딩 상태 시작
            st.session_state.is_loading = True
            
            # 질문 처리
            start_time = time.time()
            
            # 프로그레스 바와 로딩 메시지 표시
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # 단계별 진행 상황 표시
            steps = [
                "🔄 질문 분석 중...",
                "🔄 지식베이스 검색 중...",
                "🔄 AI 모델 처리 중...",
                "🔄 답변 생성 중...",
                "✅ 완료!"
            ]
            
            # 첫 번째 단계 표시
            progress_bar.progress(0.2)
            status_text.text(steps[0])
            
            # API 호출 (실제 처리)
            response = call_api("/query", {"query": user_query, "user_data": None})
            
            # API 호출 완료 후 나머지 단계 표시
            if response:
                progress_bar.progress(0.6)
                status_text.text(steps[2])
                time.sleep(0.3)
                
                progress_bar.progress(0.8)
                status_text.text(steps[3])
                time.sleep(0.2)
                
                progress_bar.progress(1.0)
                status_text.text(steps[4])
            else:
                # API 호출 실패 시
                progress_bar.progress(1.0)
                status_text.text("❌ 처리 실패")
            
            elapsed_time = time.time() - start_time
            
            # 로딩 상태 종료
            st.session_state.is_loading = False
            
            if response and "answer" in response:
                # 답변 내용 추출
                answer_text = response["answer"]
                
                # 문자열이 아닌 경우 문자열로 변환
                if not isinstance(answer_text, str):
                    answer_text = str(answer_text)
                
                # 딕셔너리 형태의 문자열인 경우 실제 내용만 추출
                if answer_text.startswith("{'answer': '") or answer_text.startswith('{"answer": "'):
                    # JSON 형태의 문자열에서 실제 답변만 추출
                    try:
                        import json
                        import ast
                        # 먼저 ast.literal_eval로 파싱 시도
                        try:
                            parsed = ast.literal_eval(answer_text)
                            if isinstance(parsed, dict) and "answer" in parsed:
                                answer_text = parsed["answer"]
                        except:
                            # JSON 파싱 시도
                            try:
                                parsed = json.loads(answer_text)
                                if isinstance(parsed, dict) and "answer" in parsed:
                                    answer_text = parsed["answer"]
                            except:
                                # 파싱 실패 시 원본 사용
                                pass
                    except:
                        pass
                

                # 채팅 히스토리에 추가
                st.session_state.chat_history.append({
                    "user": user_query,
                    "ai": answer_text,
                    "timestamp": datetime.now().strftime("%H:%M"),
                    "agent_type": response.get("agent_type", "unknown")
                })
                
                # 답변 표시
                st.success(f"✅ 답변 완료! (소요시간: {elapsed_time:.2f}초)")
                
                # 답변 내용 표시
                st.markdown("---")
                st.markdown("### 🤖 AI 답변")
                
                # 줄바꿈과 HTML 태그 처리
                if answer_text:
                    # 이스케이프된 \n을 실제 줄바꿈으로 변환
                    formatted_answer = answer_text.replace("\\n", "\n")
                    
                    # 마크다운 형식으로 변환
                    # ### 제목 형식을 HTML로 변환
                    formatted_answer = formatted_answer.replace("### ", "<h3>").replace("\n", "</h3>\n")
                    
                    # 번호가 있는 목록 처리
                    import re
                    formatted_answer = re.sub(r'(\d+)\.\s+', r'<strong>\1.</strong> ', formatted_answer)
                    
                    # 줄바꿈을 HTML로 변환
                    formatted_answer = formatted_answer.replace("\n\n", "</p><p>")
                    formatted_answer = formatted_answer.replace("\n", "<br>")
                    
                    # HTML 태그로 감싸기
                    formatted_answer = f"<p>{formatted_answer}</p>"
                    
                    st.markdown(formatted_answer, unsafe_allow_html=True)
                else:
                    st.write("답변을 생성할 수 없습니다.")
                
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
                
                # 입력 필드 초기화
                st.session_state.user_query = ""
                
            elif response and "response" in response:
                # 답변 내용 추출
                response_text = response["response"]
                
                # 문자열이 아닌 경우 문자열로 변환
                if not isinstance(response_text, str):
                    response_text = str(response_text)
                
                # 딕셔너리 형태의 문자열인 경우 실제 내용만 추출
                if response_text.startswith("{'answer': '") or response_text.startswith('{"answer": "'):
                    # JSON 형태의 문자열에서 실제 답변만 추출
                    try:
                        import json
                        import ast
                        # 먼저 ast.literal_eval로 파싱 시도
                        try:
                            parsed = ast.literal_eval(response_text)
                            if isinstance(parsed, dict) and "answer" in parsed:
                                response_text = parsed["answer"]
                        except:
                            # JSON 파싱 시도
                            try:
                                parsed = json.loads(response_text)
                                if isinstance(parsed, dict) and "answer" in parsed:
                                    response_text = parsed["answer"]
                            except:
                                # 파싱 실패 시 원본 사용
                                pass
                    except:
                        pass
                
                # 이전 API 응답 형식 지원
                st.session_state.chat_history.append({
                    "user": user_query,
                    "ai": response_text,
                    "timestamp": datetime.now().strftime("%H:%M"),
                    "agent_type": "comprehensive"
                })
                
                st.success(f"✅ 답변 완료! (소요시간: {elapsed_time:.2f}초)")
                st.markdown("---")
                st.markdown("### 🤖 AI 답변")
                
                # 줄바꿈과 HTML 태그 처리
                if response_text:
                    # 이스케이프된 \n을 실제 줄바꿈으로 변환
                    formatted_response = response_text.replace("\\n", "\n")
                    
                    # 마크다운 형식으로 변환
                    # ### 제목 형식을 HTML로 변환
                    formatted_response = formatted_response.replace("### ", "<h3>").replace("\n", "</h3>\n")
                    
                    # 번호가 있는 목록 처리
                    import re
                    formatted_response = re.sub(r'(\d+)\.\s+', r'<strong>\1.</strong> ', formatted_response)
                    
                    # 줄바꿈을 HTML로 변환
                    formatted_response = formatted_response.replace("\n\n", "</p><p>")
                    formatted_response = formatted_response.replace("\n", "<br>")
                    
                    # HTML 태그로 감싸기
                    formatted_response = f"<p>{formatted_response}</p>"
                    
                    st.markdown(formatted_response, unsafe_allow_html=True)
                else:
                    st.write("답변을 생성할 수 없습니다.")
                st.info("답변 제공: 🤖 종합 분석")
                st.session_state.user_query = ""
                
            else:
                st.error("❌ 답변을 생성할 수 없습니다.")
                
                # 상세한 에러 정보 표시
                st.markdown("---")
                st.markdown("### 🔍 오류 상세 정보")
                
                if response is None:
                    st.error("**API 서버 연결 실패**")
                    st.write("""
                    **가능한 원인:**
                    1. API 서버가 실행되지 않음 (포트 8000)
                    2. 네트워크 연결 문제
                    3. 서버 타임아웃
                    
                    **해결 방법:**
                    1. `02_start_app.bat` 실행하여 API 서버 시작
                    2. 브라우저에서 `http://localhost:8000/health` 접속 확인
                    3. 서버 로그 확인
                    """)
                elif isinstance(response, dict):
                    if "error" in response:
                        st.error(f"**API 오류:** {response['error']}")
                    elif "detail" in response:
                        st.error(f"**서버 오류:** {response['detail']}")
                    else:
                        st.error(f"**예상치 못한 응답:** {response}")
                else:
                    st.error(f"**응답 형식 오류:** {type(response)}")
                    st.write(f"**응답 내용:** {response}")
                
                # 디버깅 정보
                st.markdown("### 🛠️ 디버깅 정보")
                st.write(f"**API URL:** {API_BASE_URL}/query")
                st.write(f"**요청 시간:** {elapsed_time:.2f}초")
                st.write(f"**API 타임아웃:** {API_TIMEOUT}초")
                
                # 로그 파일 확인 안내
                st.markdown("### 📋 로그 확인")
                st.info("""
                **서버 로그 확인 방법:**
                1. `logs/app.log` 파일 확인
                2. `logs/streamlit_app.log` 파일 확인
                3. 터미널에서 API 서버 로그 확인
                """)
        else:
            st.warning("⚠️ 질문을 입력해주세요.")
    
    # 채팅 히스토리
    if st.session_state.chat_history:
        st.markdown("---")
        st.subheader("💬 대화 기록")
        
        # 히스토리 관리 버튼
        col1, col2 = st.columns([1, 4])
        with col1:
            if st.button("🗑️ 히스토리 초기화", type="secondary", disabled=st.session_state.is_loading):
                st.session_state.chat_history = []
                st.success("✅ 대화 기록이 초기화되었습니다.")
        
        with col2:
            st.caption(f"총 {len(st.session_state.chat_history)}개의 대화 기록")
        
        # 최신 대화부터 표시
        for i, chat in enumerate(reversed(st.session_state.chat_history[-10:])):  # 최근 10개만 표시
            with st.expander(f"💬 {chat['timestamp']} - {chat['user'][:50]}..."):
                st.write(f"**사용자:** {chat['user']}")
                
                # AI 답변 포맷팅
                ai_response = chat['ai']
                if ai_response:
                    # 이스케이프된 \n을 실제 줄바꿈으로 변환
                    formatted_ai = ai_response.replace("\\n", "\n")
                    
                    # 마크다운 형식으로 변환
                    # ### 제목 형식을 HTML로 변환
                    formatted_ai = formatted_ai.replace("### ", "<h3>").replace("\n", "</h3>\n")
                    
                    # 번호가 있는 목록 처리
                    import re
                    formatted_ai = re.sub(r'(\d+)\.\s+', r'<strong>\1.</strong> ', formatted_ai)
                    
                    # 줄바꿈을 HTML로 변환
                    formatted_ai = formatted_ai.replace("\n\n", "</p><p>")
                    formatted_ai = formatted_ai.replace("\n", "<br>")
                    
                    # HTML 태그로 감싸기
                    formatted_ai = f"<p>{formatted_ai}</p>"
                    
                    st.markdown(f"**AI:** {formatted_ai}", unsafe_allow_html=True)
                else:
                    st.write(f"**AI:** {ai_response}")
                
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
    else:
        st.info("💡 아직 대화 기록이 없습니다. 질문을 해보세요!")

def render_portfolio_simulation_tab():
    """포트폴리오 시뮬레이션 탭"""
    st.header("📈 포트폴리오 시뮬레이션")
    
    st.info("💡 다양한 포트폴리오 구성을 시뮬레이션하여 최적의 투자 전략을 찾아보세요.")
    
    # 포트폴리오 설정
    st.subheader("🎯 포트폴리오 설정")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # 종목 선택
        st.write("**📊 종목 선택**")
        symbols_input = st.text_area(
            "종목 코드 (한 줄에 하나씩)",
            value="005930.KS\n000660.KS\n035420.KS\n051910.KS\n006400.KS",
            height=100,
            help="야후 파이낸스 종목 코드를 입력하세요. 예: 005930.KS (삼성전자)"
        )
        
        # 투자 기간
        st.write("**📅 투자 기간**")
        start_date = st.date_input("시작일", value=datetime(2023, 1, 1))
        end_date = st.date_input("종료일", value=datetime.now())
        
    with col2:
        # 투자 금액
        st.write("**💰 투자 금액**")
        initial_investment = st.number_input(
            "초기 투자 금액 (원)",
            min_value=1000000,
            value=10000000,
            step=1000000,
            format="%d"
        )
        
        # 포트폴리오 수
        st.write("**📊 시뮬레이션 설정**")
        num_portfolios = st.slider("포트폴리오 수", min_value=100, max_value=1000, value=500, step=100)
        
        # 위험 성향
        risk_tolerance = st.selectbox(
            "위험 성향",
            ["conservative", "moderate", "aggressive"],
            format_func=lambda x: {"conservative": "보수적", "moderate": "중립적", "aggressive": "공격적"}[x]
        )
    
    # 시뮬레이션 실행
    if st.button("🚀 포트폴리오 시뮬레이션 실행", type="primary"):
        if symbols_input.strip():
            symbols = [s.strip() for s in symbols_input.split('\n') if s.strip()]
            
            # 로딩 상태 시작
            st.session_state.is_loading = True
            
            # 프로그레스 바와 로딩 메시지 표시
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # 단계별 진행 상황 표시
            steps = [
                "🔄 포트폴리오 시뮬레이션 시작...",
                "🔄 주가 데이터 수집 중...",
                "🔄 효율적 프론티어 계산 중...",
                "🔄 최적 포트폴리오 분석 중...",
                "🔄 결과 시각화 중...",
                "✅ 완료!"
            ]
            
            # 첫 번째 단계 표시
            progress_bar.progress(0.1)
            status_text.text(steps[0])
            
            # 효율적 프론티어 생성
            efficient_frontier_data = {
                "symbols": symbols,
                "start_date": start_date.strftime('%Y-%m-%d'),
                "end_date": end_date.strftime('%Y-%m-%d'),
                "num_portfolios": num_portfolios
            }
            
            # API 호출 (실제 처리)
            response = call_api("/portfolio/efficient-frontier", efficient_frontier_data)
            
            # API 호출 완료 후 나머지 단계 표시
            if response:
                progress_bar.progress(0.3)
                status_text.text(steps[1])
                time.sleep(0.2)
                
                progress_bar.progress(0.5)
                status_text.text(steps[2])
                time.sleep(0.2)
                
                progress_bar.progress(0.7)
                status_text.text(steps[3])
                time.sleep(0.2)
                
                progress_bar.progress(0.9)
                status_text.text(steps[4])
                time.sleep(0.2)
                
                progress_bar.progress(1.0)
                status_text.text(steps[5])
            else:
                # API 호출 실패 시
                progress_bar.progress(1.0)
                status_text.text("❌ 시뮬레이션 실패")
            
            # 로딩 상태 종료
            st.session_state.is_loading = False
            
            if response and "error" not in response:
                st.success("✅ 포트폴리오 시뮬레이션이 완료되었습니다!")
                
                # 결과 표시
                st.subheader("📊 시뮬레이션 결과")
                
                # 효율적 프론티어 차트
                if "portfolios" in response:
                    portfolios = response["portfolios"]
                    
                                            # 산점도 차트 생성
                        if PLOTLY_AVAILABLE:
                            returns = [p["return"] for p in portfolios]
                            volatilities = [p["volatility"] for p in portfolios]
                            
                            fig = px.scatter(
                                x=volatilities,
                                y=returns,
                                title="효율적 프론티어",
                                labels={"x": "변동성 (리스크)", "y": "기대 수익률"},
                                color_discrete_sequence=['blue']
                            )
                            
                            fig.update_layout(
                                height=500,
                                showlegend=False
                            )
                            
                            st.plotly_chart(fig, use_container_width=True)
                        else:
                            st.warning("plotly가 설치되지 않아 차트를 표시할 수 없습니다.")
                            # 대신 데이터 테이블로 표시
                            st.write("**포트폴리오 데이터:**")
                            portfolio_df = pd.DataFrame(portfolios)
                            st.dataframe(portfolio_df[["return", "volatility"]].head(10))
                    
                    # 최적 포트폴리오 정보
                    if "optimal_portfolio" in response:
                        optimal = response["optimal_portfolio"]
                        st.subheader("🎯 최적 포트폴리오")
                        
                        col1, col2, col3, col4 = st.columns(4)
                        with col1:
                            st.metric("기대 수익률", f"{optimal.get('return', 0):.2f}%")
                        with col2:
                            st.metric("변동성", f"{optimal.get('volatility', 0):.2f}%")
                        with col3:
                            st.metric("샤프 비율", f"{optimal.get('sharpe_ratio', 0):.2f}")
                        with col4:
                            st.metric("최대 낙폭", f"{optimal.get('max_drawdown', 0):.2f}%")
                        
                        # 자산 배분
                        st.write("**📊 자산 배분**")
                        allocation_data = optimal.get("allocation", {})
                        if allocation_data:
                            allocation_df = pd.DataFrame([
                                {"종목": symbol, "비중": f"{weight:.1f}%"}
                                for symbol, weight in allocation_data.items()
                            ])
                            st.dataframe(allocation_df, use_container_width=True)
                else:
                    st.error("❌ 포트폴리오 시뮬레이션에 실패했습니다.")
                    if response and "detail" in response:
                        st.error(f"오류 상세: {response['detail']}")
                    else:
                        st.error("API 서버에서 응답을 받지 못했습니다.")
        else:
            st.warning("⚠️ 종목 코드를 입력해주세요.")

def render_investment_analysis_tab():
    """투자 분석 탭"""
    st.header("🎯 투자 분석")
    
    st.info("💡 개별 종목 분석과 시장 예측을 통해 투자 결정을 도와드립니다.")
    
    # 종목 분석
    st.subheader("📊 종목 분석")
    
    col1, col2 = st.columns(2)
    
    with col1:
        symbol = st.text_input(
            "종목 코드",
            value="005930.KS",
            help="야후 파이낸스 종목 코드를 입력하세요. 예: 005930.KS (삼성전자)"
        )
        
        analysis_type = st.selectbox(
            "분석 유형",
            ["sentiment", "prediction"],
            format_func=lambda x: {"sentiment": "감정 분석", "prediction": "시장 예측"}[x]
        )
    
    with col2:
        if analysis_type == "prediction":
            days = st.slider("예측 기간 (일)", min_value=7, max_value=90, value=30)
            confidence_level = st.slider("신뢰도", min_value=0.5, max_value=0.95, value=0.8, step=0.05)
    
    # 분석 실행
    if st.button("🔍 투자 분석 실행", type="primary"):
        if symbol.strip():
            # 로딩 상태 시작
            st.session_state.is_loading = True
            
            # 프로그레스 바와 로딩 메시지 표시
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # 단계별 진행 상황 표시
            steps = [
                "🔄 투자 분석 시작...",
                "🔄 데이터 수집 중...",
                "🔄 분석 처리 중...",
                "🔄 결과 생성 중...",
                "✅ 완료!"
            ]
            
            # 첫 번째 단계 표시
            progress_bar.progress(0.2)
            status_text.text(steps[0])
            
            if analysis_type == "sentiment":
                    # 감정 분석
                    sentiment_data = {
                        "text_data": [f"분석 대상: {symbol}"]
                    }
                    response = call_api("/ai/sentiment-analysis", sentiment_data)
                    
                    if response and "error" not in response:
                        st.success("✅ 감정 분석이 완료되었습니다!")
                        
                        # 결과 표시
                        sentiment_score = response.get("overall_sentiment", 0)
                        sentiment_label = response.get("sentiment_label", "중립")
                        
                        st.subheader("📊 감정 분석 결과")
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            st.metric("감정 점수", f"{sentiment_score:.2f}")
                        with col2:
                            st.metric("감정 레이블", sentiment_label)
                        
                        # 감정 점수 시각화
                        if PLOTLY_AVAILABLE:
                            fig = go.Figure(go.Indicator(
                                mode="gauge+number+delta",
                                value=sentiment_score,
                                domain={'x': [0, 1], 'y': [0, 1]},
                                title={'text': "시장 감정 지수"},
                                delta={'reference': 0},
                                gauge={
                                    'axis': {'range': [-1, 1]},
                                    'bar': {'color': "darkblue"},
                                    'steps': [
                                        {'range': [-1, -0.3], 'color': "lightgray"},
                                        {'range': [-0.3, 0.3], 'color': "yellow"},
                                        {'range': [0.3, 1], 'color': "lightgreen"}
                                    ],
                                    'threshold': {
                                        'line': {'color': "red", 'width': 4},
                                        'thickness': 0.75,
                                        'value': 0.8
                                    }
                                }
                            ))
                            
                            fig.update_layout(height=400)
                            st.plotly_chart(fig, use_container_width=True)
                        else:
                            st.warning("plotly가 설치되지 않아 게이지 차트를 표시할 수 없습니다.")
                            # 대신 간단한 텍스트로 표시
                            st.write(f"**감정 점수:** {sentiment_score:.2f}")
                            if sentiment_score > 0.3:
                                st.success("긍정적")
                            elif sentiment_score < -0.3:
                                st.error("부정적")
                            else:
                                st.info("중립적")
                        
            else:
                # 시장 예측
                response = call_api(f"/ai/market-prediction/{symbol}?days={days}&confidence_level={confidence_level}")
                
                if response and "error" not in response:
                        st.success("✅ 시장 예측이 완료되었습니다!")
                        
                        # 결과 표시
                        st.subheader("🔮 시장 예측 결과")
                        
                        prediction = response.get("trend_direction", "상승")
                        confidence = response.get("confidence_level", 0)
                        risk_level = response.get("risk_level", "보통")
                        recommendation = response.get("recommendation", "")
                        
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("예측 방향", prediction)
                        with col2:
                            st.metric("신뢰도", f"{confidence:.1f}%")
                        with col3:
                            st.metric("리스크 레벨", risk_level)
                        
                        if recommendation:
                            st.write("**💡 투자 권고사항**")
                            st.info(recommendation)
                else:
                    st.error("❌ 시장 예측에 실패했습니다.")
        else:
            st.warning("⚠️ 종목 코드를 입력해주세요.")

def render_comprehensive_analysis_tab():
    """종합 분석 탭"""
    st.header("📊 종합 분석")
    
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
        
        # 종합분석 실행 버튼
        if st.form_submit_button("🤖 종합분석 실행", type="primary", use_container_width=True):
            # 사용자 데이터 구성
            user_data = {
                "age": age,
                "income": income,
                "expenses": expenses,
                "savings": savings,
                "risk_tolerance": risk_tolerance
            }
            
            # 세션에 저장
            st.session_state.user_data = user_data
            
            # 종합분석 실행
            st.session_state.quick_analysis = "detailed"
            st.session_state.ai_consultation_auto_submit = True
            
            # 분석 질문 생성
            analysis_query = f"""
            종합적인 재무 분석을 해주세요.
            
            기본 정보:
            - 나이: {age}세
            - 연소득: {income:,}원
            - 연지출: {expenses:,}원
            - 현재 저축액: {savings:,}원
            - 위험 성향: {risk_tolerance}
            
            다음 영역을 종합적으로 분석해주세요:
            1. 예산 관리 및 재무 건강도
            2. 투자 포트폴리오 구성
            3. 세금 절약 전략
            4. 은퇴 준비 계획
            5. 위험 관리 방안
            """
            
            st.session_state.user_query = analysis_query
            
            # 종합분석 바로 실행
            st.success("✅ 종합분석을 시작합니다...")
            
            # 로딩 상태 시작
            st.session_state.is_loading = True
            
            # 프로그레스 바와 로딩 메시지 표시
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # 단계별 진행 상황 표시
            steps = [
                "🔄 종합분석 시작...",
                "🔄 재무 건강도 분석 중...",
                "🔄 투자 포트폴리오 구성 중...",
                "🔄 세금 절약 전략 분석 중...",
                "🔄 은퇴 준비 계획 수립 중...",
                "✅ 완료!"
            ]
            
            # 첫 번째 단계 표시
            progress_bar.progress(0.1)
            status_text.text(steps[0])
            
            # API 호출 (실제 처리)
            response = call_api("/query", {"query": analysis_query, "user_data": user_data})
            
            # API 호출 완료 후 나머지 단계 표시
            if response:
                progress_bar.progress(0.3)
                status_text.text(steps[1])
                time.sleep(0.2)
                
                progress_bar.progress(0.5)
                status_text.text(steps[2])
                time.sleep(0.2)
                
                progress_bar.progress(0.7)
                status_text.text(steps[3])
                time.sleep(0.2)
                
                progress_bar.progress(0.9)
                status_text.text(steps[4])
                time.sleep(0.2)
                
                progress_bar.progress(1.0)
                status_text.text(steps[5])
            else:
                # API 호출 실패 시
                progress_bar.progress(1.0)
                status_text.text("❌ 분석 실패")
            
            # 로딩 상태 종료
            st.session_state.is_loading = False
            
            if response and "answer" in response:
                # 답변 내용 추출
                answer_text = response["answer"]
                
                # 문자열이 아닌 경우 문자열로 변환
                if not isinstance(answer_text, str):
                    answer_text = str(answer_text)
                
                # 딕셔너리 형태의 문자열인 경우 실제 내용만 추출
                if answer_text.startswith("{'answer': '") or answer_text.startswith('{"answer": "'):
                    try:
                        import json
                        import ast
                        try:
                            parsed = ast.literal_eval(answer_text)
                            if isinstance(parsed, dict) and "answer" in parsed:
                                answer_text = parsed["answer"]
                        except:
                            try:
                                parsed = json.loads(answer_text)
                                if isinstance(parsed, dict) and "answer" in parsed:
                                    answer_text = parsed["answer"]
                            except:
                                pass
                    except:
                        pass
                
                # 결과 표시
                st.success("✅ 종합분석이 완료되었습니다!")
                st.subheader("📊 종합 재무 분석 결과")
                st.markdown(answer_text)
                
                # 채팅 히스토리에 추가
                st.session_state.chat_history.append({
                    "user": analysis_query,
                    "ai": answer_text,
                    "timestamp": datetime.now().strftime("%H:%M"),
                    "type": "comprehensive_analysis"
                })
            else:
                st.error("❌ 종합분석에 실패했습니다.")
                if response and "detail" in response:
                    st.error(f"오류 상세: {response['detail']}")

def main():
    """메인 함수"""
    # 헤더 최적화
    st.title("💰 AI 재무관리 어드바이저")
    
    # API 상태 확인 (실시간)
    with st.spinner("API 서버 연결 확인 중..."):
        api_healthy = check_api_health()
        st.session_state.api_healthy = api_healthy
    
    if not api_healthy:
        st.error("⚠️ API 서버에 연결할 수 없습니다.")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🔧 문제 해결 방법")
            st.write("""
            1. **02_start_app.bat**를 다시 실행해보세요
            2. API 서버 창이 정상적으로 열렸는지 확인하세요
            3. 회사 Azure OpenAI 서비스 연결을 기다려주세요 (1-2분 소요)
            4. 포트 8000이 다른 프로그램에서 사용 중인지 확인하세요
            5. 방화벽 설정을 확인하세요
            """)
            
            st.subheader("🔍 Azure OpenAI 설정 확인")
            st.write("""
            AI 상담이 작동하지 않는 경우:
            1. .env 파일에서 다음 설정을 확인하세요:
               - AOAI_ENDPOINT=https://your-resource.openai.azure.com/
               - AOAI_API_KEY=your_azure_openai_api_key_here
               - AOAI_DEPLOY_EMBED_3_SMALL=text-embedding-3-small
            2. Azure OpenAI Studio에서 임베딩 모델이 올바르게 배포되었는지 확인하세요
            3. 배포 이름이 .env 파일의 AOAI_DEPLOY_EMBED_3_SMALL과 일치하는지 확인하세요
            """)
        
        with col2:
            st.subheader("📋 수동 실행 방법")
            st.code("""
# API 서버 실행
python -m uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload

# Streamlit 실행 (새 터미널에서)
python -m streamlit run main.py --server.port 8501
            """)
        
        st.info("💡 회사 Azure OpenAI 서비스 사용 시 첫 연결에 시간이 걸릴 수 있습니다.")
        
        # API 서버가 없을 때 안내
        st.warning("API 서버가 실행되지 않아 일부 기능을 사용할 수 없습니다.")
        st.info("💡 API 서버를 시작한 후 다시 시도해주세요.")
        return
    
    st.success("✅ API 서버에 연결되었습니다!")
    
    # 실시간 시장 대시보드 표시
    create_market_dashboard()
    
    # 탭 생성 (개선된 기능)
    tab_names = ["💬 AI 상담", "📊 종합 분석", "📈 포트폴리오 시뮬레이션", "🎯 투자 분석"]
    tabs = st.tabs(tab_names)
    
    # AI 상담 탭
    with tabs[0]:
        render_ai_consultation_tab()
    
    # 종합 분석 탭
    with tabs[1]:
        render_comprehensive_analysis_tab()
    
    # 포트폴리오 시뮬레이션 탭
    with tabs[2]:
        render_portfolio_simulation_tab()
    
    # 투자 분석 탭
    with tabs[3]:
        render_investment_analysis_tab()

if __name__ == "__main__":
    main()
