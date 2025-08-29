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
API_TIMEOUT = int(os.getenv("API_TIMEOUT", "30"))  # 타임아웃 증가 (지식베이스 초기화 시간 고려)
CACHE_TTL = int(os.getenv("CACHE_TTL", "300"))

# API 연결 재시도 설정 (최적화)
API_RETRY_COUNT = 2  # 재시도 횟수 증가
API_RETRY_DELAY = 1.0  # 재시도 간격 증가

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
@st.cache_data(ttl=30)  # 30초 캐시
def check_api_health():
    """API 서버 상태 확인"""
    result = make_api_request("GET", "/health", timeout=5)  # 타임아웃 단축
    return result is not None

@st.cache_data(ttl=10)  # 10초 캐시
def call_api(endpoint, data=None):
    """API 호출"""
    if data:
        return make_api_request("POST", endpoint, data)
    else:
        return make_api_request("GET", endpoint)

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

def render_ai_consultation_tab():
    """AI 상담 탭"""
    st.header("💬 AI 상담")
    
    # 기능 차별화 설명
    st.info("""
    **🎯 기능별 차이점:**
    
    **📝 샘플 질문**: 일반적인 재무 상담 질문으로 간단한 답변을 제공합니다.
    
    **💭 직접 질문**: 사용자가 원하는 내용을 자유롭게 질문할 수 있습니다.
    
    **💡 팁**: 더 정확한 분석을 위해 종합 분석 탭에서 먼저 개인 정보를 입력하세요!
    """)
    
    # 샘플 질문 버튼들
    st.subheader("📝 샘플 질문")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("💰 예산 관리 방법", use_container_width=True, disabled=st.session_state.is_loading):
            st.session_state.user_query = "월급의 30%를 저축하려고 하는데, 어떤 방법으로 예산을 관리하면 좋을까요?"
            st.session_state.auto_submit = True
        
        if st.button("📈 투자 포트폴리오", use_container_width=True, disabled=st.session_state.is_loading):
            st.session_state.user_query = "초보 투자자로서 안전하면서도 수익을 낼 수 있는 포트폴리오를 추천해주세요."
            st.session_state.auto_submit = True
    
    with col2:
        if st.button("🧾 세금 절약 전략", use_container_width=True, disabled=st.session_state.is_loading):
            st.session_state.user_query = "연말정산에서 세금을 절약할 수 있는 방법들을 알려주세요."
            st.session_state.auto_submit = True
        
        if st.button("🎯 은퇴 계획", use_container_width=True, disabled=st.session_state.is_loading):
            st.session_state.user_query = "30대 후반인데 은퇴를 위해 얼마나 저축해야 하고 어떤 준비를 해야 할까요?"
            st.session_state.auto_submit = True
    
    with col3:
        if st.button("🏠 부동산 투자", use_container_width=True, disabled=st.session_state.is_loading):
            st.session_state.user_query = "부동산 투자를 고려하고 있는데, 현재 시점에서 어떤 지역이나 유형이 좋을까요?"
            st.session_state.auto_submit = True
        
        if st.button("💳 신용카드 관리", use_container_width=True, disabled=st.session_state.is_loading):
            st.session_state.user_query = "신용카드를 효율적으로 사용하면서 신용점수를 관리하는 방법을 알려주세요."
            st.session_state.auto_submit = True
    
    # 사용자 입력
    st.subheader("💭 질문하기")
    user_query = st.text_area(
        "재무 관련 질문을 입력하세요:",
        value=st.session_state.user_query,
        height=100,
        placeholder="예: 월급의 30%를 저축하려고 하는데, 어떤 방법으로 예산을 관리하면 좋을까요?"
    )
    
    # 질문하기 버튼
    col1, col2 = st.columns([1, 4])
    with col1:
        submit_button = st.button("🤖 AI에게 질문하기", type="primary", disabled=st.session_state.is_loading)
    
    with col2:
        if st.button("🗑️ 입력 초기화", type="secondary", disabled=st.session_state.is_loading):
            st.session_state.user_query = ""
    
    # 질문 처리
    if submit_button or st.session_state.auto_submit:
        if user_query.strip():
            # 자동 제출 상태 초기화
            st.session_state.auto_submit = False
            
            # 로딩 상태 시작
            st.session_state.is_loading = True
            
            # 질문 처리
            start_time = time.time()
            
            # 프로그레스 바와 로딩 메시지 표시
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # 단계별 진행 상황 표시
            steps = [
                "🔍 질문 분석 중...",
                "📚 지식베이스 검색 중...",
                "🤖 AI 모델 처리 중...",
                "📝 답변 생성 중...",
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

def render_comprehensive_analysis_tab():
    """종합 분석 탭"""
    st.header("📊 종합 분석")
    
    st.info("💡 이 기능은 사용자의 재무 정보를 종합적으로 분석하여 맞춤형 조언을 제공합니다.")
    
    # 빠른 분석 섹션
    st.subheader("🚀 빠른 분석")
    st.info("""
    **🚀 빠른 분석**: 전문 에이전트가 구조화된 상세 분석을 수행합니다.
    - 예산 분석: 재무 건강도, 지출 패턴 분석, 최적화 방안
    - 투자 자문: 포트폴리오 구성, 리스크 관리, 수익률 예측
    - 세금 절약: 공제 항목 분석, 최적화 전략, 절약 효과 계산
    
    **💡 차이점**: 상세/요약 분석은 종합적인 재무 진단을, 빠른 분석은 특정 영역에 집중한 전문 분석을 제공합니다.
    """)
    
    # 사용자 데이터 확인
    user_data = st.session_state.get('user_data', {})
    has_user_data = bool(user_data and user_data.get('income', 0) > 0)
    
    if has_user_data:
        st.success("✅ 사용자 데이터가 입력되어 있습니다. 실제 데이터로 분석을 수행합니다.")
        income = user_data.get('income', 0)
        expenses = user_data.get('expenses', 0)
        age = user_data.get('age', 30)
        risk_tolerance = user_data.get('risk_tolerance', 'moderate')
        
        # 실제 데이터로 질문 생성
        budget_query = f"전문적인 예산 분석을 해주세요. 연소득 {income:,}원, 연지출 {expenses:,}원인 상황에서 예산 최적화 방안과 재무 건강도를 평가해주세요."
        investment_query = f"전문적인 투자 자문을 해주세요. {age}세, {risk_tolerance} 위험성향, 투자 가능 금액 {(income-expenses)//12:,}원으로 포트폴리오 구성과 리스크 관리 방안을 제시해주세요."
        tax_query = f"전문적인 세금 절약 분석을 해주세요. 연소득 {income:,}원인 상황에서 최적의 세금 절약 전략을 제시해주세요."
    else:
        st.warning("⚠️ 예시 데이터로 분석을 수행합니다.")
        st.info("💡 **정확한 데이터를 원하시면, 아래 기본정보/월별지출을 먼저 입력해 주세요.**")
        # 기본 예시 데이터
        budget_query = "전문적인 예산 분석을 해주세요. 월급 500만원, 월 지출 300만원, 저축 목표 200만원인 상황에서 예산 최적화 방안과 재무 건강도를 평가해주세요."
        investment_query = "전문적인 투자 자문을 해주세요. 초보 투자자, 30대, 위험 성향 중간, 투자 금액 1000만원으로 포트폴리오 구성과 리스크 관리 방안을 제시해주세요."
        tax_query = "전문적인 세금 절약 분석을 해주세요. 연소득 6000만원, 신용카드 사용액 200만원, 의료비 50만원, 보험료 30만원인 상황에서 최적의 세금 절약 전략을 제시해주세요."
    
    quick_col1, quick_col2, quick_col3 = st.columns(3)
    
    with quick_col1:
        if st.button("💰 예산 분석", use_container_width=True, type="primary", disabled=st.session_state.is_loading):
            st.session_state.user_query = budget_query
            st.session_state.auto_submit = True
            st.session_state.analysis_type = "budget"
    
    with quick_col2:
        if st.button("📈 투자 자문", use_container_width=True, type="primary", disabled=st.session_state.is_loading):
            st.session_state.user_query = investment_query
            st.session_state.auto_submit = True
            st.session_state.analysis_type = "investment"
    
    with quick_col3:
        if st.button("🧾 세금 절약", use_container_width=True, type="primary", disabled=st.session_state.is_loading):
            st.session_state.user_query = tax_query
            st.session_state.auto_submit = True
            st.session_state.analysis_type = "tax"
    
    st.markdown("---")
    
    # 종합 분석 옵션
    st.subheader("⚡ 종합 분석 옵션")
    st.info("💡 상세 분석은 포괄적인 재무 진단을, 요약 분석은 핵심 내용만 간단히 제공합니다.")
    
    quick_analysis_col1, quick_analysis_col2 = st.columns(2)
    
    with quick_analysis_col1:
        if st.button("📈 상세 분석", use_container_width=True, type="primary", disabled=st.session_state.is_loading):
            st.session_state.quick_analysis = "detailed"
    
    with quick_analysis_col2:
        if st.button("📋 요약 분석", use_container_width=True, type="secondary", disabled=st.session_state.is_loading):
            st.session_state.quick_analysis = "summary"
    
    st.markdown("---")
    
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
        
        submitted = st.form_submit_button("📊 종합 분석 실행", type="primary", disabled=st.session_state.is_loading)
        
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
            
            # 세션 상태에 사용자 데이터 저장 (빠른 시작에서 사용)
            st.session_state.user_data = user_data
            
            # 분석 요청
            start_time = time.time()
            
            with st.spinner("종합 분석을 수행하고 있습니다..."):
                response = call_api("/comprehensive-analysis", {"user_data": user_data})
            
            elapsed_time = time.time() - start_time
            
            if response and "analysis" in response:
                st.success(f"✅ 분석 완료! (소요시간: {elapsed_time:.2f}초)")
                
                # 분석 결과 표시
                analysis = response["analysis"]
                
                # 분석 유형에 따른 표시
                analysis_type = st.session_state.get('quick_analysis', 'detailed')
                
                if analysis_type == "summary":
                    # 요약 분석 표시
                    st.subheader("📋 분석 요약")
                    
                    # 핵심 지표
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("연소득", f"₩{income:,.0f}")
                    with col2:
                        st.metric("연지출", f"₩{expenses:,.0f}")
                    with col3:
                        net_income = income - expenses
                        st.metric("순소득", f"₩{net_income:,.0f}")
                    with col4:
                        savings_rate = (net_income / income) * 100 if income > 0 else 0
                        st.metric("저축률", f"{savings_rate:.1f}%")
                    
                    # 핵심 권장사항만 표시
                    if "recommendations" in analysis:
                        st.subheader("💡 핵심 권장사항")
                        recommendations = analysis["recommendations"]
                        if isinstance(recommendations, str):
                            # 문자열인 경우 줄바꿈으로 분리
                            rec_list = [rec.strip() for rec in recommendations.split('\n') if rec.strip()]
                        else:
                            rec_list = recommendations[:3]  # 상위 3개만
                        
                        for i, rec in enumerate(rec_list, 1):
                            st.write(f"**{i}.** {rec}")
                    
                    # 상세 분석 보기 버튼
                    if st.button("📊 상세 분석 보기"):
                        st.session_state.show_detailed = True
                        st.rerun()
                
                else:
                    # 상세 분석 표시 (기본)
                    st.subheader("📊 상세 분석 결과")
                    
                    # 예산 분석
                    if "budget_analysis" in analysis:
                        with st.expander("💰 예산 분석", expanded=True):
                            budget_text = analysis["budget_analysis"]
                            if budget_text:
                                # 줄바꿈 처리
                                budget_text = budget_text.replace("\\n", "\n").replace("\n", "<br>")
                                st.markdown(f"<p>{budget_text}</p>", unsafe_allow_html=True)
                    
                    # 투자 분석
                    if "investment_analysis" in analysis:
                        with st.expander("📈 투자 분석", expanded=True):
                            investment_text = analysis["investment_analysis"]
                            if investment_text:
                                investment_text = investment_text.replace("\\n", "\n").replace("\n", "<br>")
                                st.markdown(f"<p>{investment_text}</p>", unsafe_allow_html=True)
                    
                    # 세금 분석
                    if "tax_analysis" in analysis:
                        with st.expander("🧾 세금 분석", expanded=True):
                            tax_text = analysis["tax_analysis"]
                            if tax_text:
                                tax_text = tax_text.replace("\\n", "\n").replace("\n", "<br>")
                                st.markdown(f"<p>{tax_text}</p>", unsafe_allow_html=True)
                    
                    # 은퇴 분석
                    if "retirement_analysis" in analysis:
                        with st.expander("🎯 은퇴 계획 분석", expanded=True):
                            retirement_text = analysis["retirement_analysis"]
                            if retirement_text:
                                retirement_text = retirement_text.replace("\\n", "\n").replace("\n", "<br>")
                                st.markdown(f"<p>{retirement_text}</p>", unsafe_allow_html=True)
                    
                    # 종합 권장사항
                    if "recommendations" in analysis:
                        st.subheader("💡 종합 권장사항")
                        recommendations_text = analysis["recommendations"]
                        if recommendations_text:
                            recommendations_text = recommendations_text.replace("\\n", "\n").replace("\n", "<br>")
                            st.markdown(f"<p>{recommendations_text}</p>", unsafe_allow_html=True)
                    
                    # 요약 보기 버튼
                    if st.button("📋 요약 보기"):
                        st.session_state.show_summary = True
                        st.rerun()
                
                # 분석 완료 메시지
                st.success("✅ 종합 분석이 완료되었습니다!")
                
            else:
                st.error("❌ 분석을 수행할 수 없습니다. API 서버를 확인해주세요.")

def main():
    """메인 함수"""
    # 헤더 최적화
    st.title("💰 AI 재무관리 어드바이저")
    
    # API 상태 확인 (단순화)
    if not st.session_state.api_checked:
        with st.spinner("API 서버 연결 확인 중..."):
            api_healthy = check_api_health()
            st.session_state.api_checked = True
            st.session_state.api_healthy = api_healthy
    else:
        api_healthy = st.session_state.api_healthy
    
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
    
    # 탭 생성 (핵심 기능만)
    tab_names = ["💬 AI 상담", "📊 종합 분석"]
    tabs = st.tabs(tab_names)
    
    # AI 상담 탭
    with tabs[0]:
        render_ai_consultation_tab()
    
    # 종합 분석 탭
    with tabs[1]:
        render_comprehensive_analysis_tab()

if __name__ == "__main__":
    main()
