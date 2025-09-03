# 💰 AI 재무관리 어드바이저

> AI 기반 개인 재무 관리 및 투자 자문 시스템

![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)
![LangChain](https://img.shields.io/badge/LangChain-0.1+-yellow.svg)
![Docker](https://img.shields.io/badge/Docker-20.10+-lightblue.svg)

## 🎯 프로젝트 개요

AI 재무관리 어드바이저는 개인의 재무 상황을 종합적으로 분석하고 맞춤형 조언을 제공하는 AI 기반 시스템입니다. LangChain과 LangGraph를 활용한 멀티 에이전트 시스템으로 예산 관리, 투자 자문, 세금 절약, 은퇴 계획 등 다양한 재무 영역을 포괄합니다.

## ✨ 주요 기능

### 🤖 AI 상담 시스템
- **빠른 분석**: 전문 에이전트가 구조화된 상세 분석 제공
- **샘플 질문**: 일반적인 재무 상담 질문에 대한 답변
- **직접 질문**: 사용자 맞춤형 자유 질문 지원
- **실시간 로딩**: 프로그레스 바와 버튼 비활성화로 UX 개선

### 📊 종합 재무 분석
- **상세 분석**: 포괄적인 재무 진단 및 권장사항
- **요약 분석**: 핵심 내용만 간단히 제공
- **사용자 데이터 기반**: 실제 개인 정보를 활용한 맞춤 분석
- **HTML 포맷팅**: 줄바꿈과 구조화된 답변 표시

### 🚀 새로운 고급 기능 (v2.0)
- **📈 실시간 재무 데이터**: 주식, 환율, 경제 지표 실시간 조회
- **📊 포트폴리오 시뮬레이션**: 투자 전략 백테스팅 및 성과 분석
- **🎯 효율적 프론티어**: 최적 포트폴리오 구성 분석
- **🤖 AI 시장 예측**: 기술적 지표 기반 트렌드 예측
- **💭 감정 분석**: 시장 뉴스 및 댓글 감정 분석
- **📱 고급 API**: RESTful API를 통한 외부 시스템 연동
- **🎨 개선된 UI/UX**: 4개 탭 구조, 실시간 대시보드, 인터랙티브 차트
- **📊 시각화**: Plotly 기반 포트폴리오 성과 차트 및 지출 분석

### 🛠️ 기술 스택
- **AI 프레임워크**: LangChain, LangGraph
- **LLM**: Azure OpenAI GPT-4
- **백엔드**: FastAPI
- **프론트엔드**: Streamlit
- **데이터베이스**: ChromaDB (벡터 DB)
- **배포**: Docker

## 🚀 빠른 시작

### 🔧 실행 모드 선택

#### 1. 간단 버전 (권장)
- **특징**: API 서버 없이 내장 로직으로 동작
- **의존성**: 최소 (streamlit, pandas, numpy, plotly만 필요)
- **사용법**: `start_simple.bat` 실행
- **접속**: http://localhost:8502

#### 2. 직접 실행 버전
- **특징**: API 서버 없이 전체 기능 사용
- **의존성**: 전체 (LangChain, Azure OpenAI 등)
- **사용법**: `start_direct.bat` 실행
- **접속**: http://localhost:8501

#### 3. 기존 API 서버 방식
- **특징**: FastAPI 서버와 Streamlit 클라이언트 분리
- **의존성**: 전체 + 네트워크 연결 필요
- **사용법**: `02_start_app.bat` 실행
- **접속**: http://localhost:8501 (UI), http://localhost:8000 (API)

### 1. 환경 설정

```bash
# 저장소 클론
git clone <repository-url>
cd AI-finance-advisor

# 환경변수 설정
cp env_example.txt .env
# .env 파일에서 Azure OpenAI 설정 입력
```

### 2. 의존성 설치

```bash
pip install -r requirements.txt
```

### 3. 실행

#### 🚀 API 서버 없이 직접 실행 (권장)
회사 개발환경에서 API 서버가 작동하지 않는 경우 사용하세요.

```bash
# 방법 1: 간단 버전 (최소 의존성)
start_simple.bat

# 방법 2: 직접 실행 버전 (전체 기능)
start_direct.bat
```

#### 방법 3: 기존 API 서버 방식
```bash
# 1. 초기 설정
01_initial_setup.bat

# 2. 애플리케이션 실행
02_start_app.bat

# 3. Docker 실행 (선택사항)
03_start_docker.bat
```

#### 방법 4: 수동 실행
```bash
# API 서버 실행
python -m uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload

# 새 터미널에서 Streamlit 실행
python -m streamlit run main.py --server.port 8501
```

### 4. 접속

#### 직접 실행 모드
- **간단 버전**: http://localhost:8502
- **직접 실행 버전**: http://localhost:8501

#### 기존 API 서버 모드
- **웹 인터페이스**: http://localhost:8501
- **API 문서**: http://localhost:8000/docs
- **새로운 API 엔드포인트**:
  - 실시간 주식 데이터: `GET /financial-data/stock/{symbol}`
  - 환율 정보: `GET /financial-data/exchange-rate`
  - 경제 지표: `GET /financial-data/economic-indicators`
  - 포트폴리오 시뮬레이션: `POST /portfolio/simulate`
  - 효율적 프론티어: `POST /portfolio/efficient-frontier`
  - 감정 분석: `POST /ai/sentiment-analysis`
  - 시장 예측: `GET /ai/market-prediction/{symbol}`

## 📋 사용 가이드

### AI 상담 사용법

1. **빠른 분석**
   - 종합분석 탭에서 개인 정보 입력 (권장)
   - 빠른 분석 버튼 클릭
   - 전문 에이전트의 구조화된 분석 결과 확인

2. **샘플 질문**
   - 미리 정의된 재무 관련 질문 선택
   - 일반적인 상담 답변 받기

3. **직접 질문**
   - 텍스트 영역에 원하는 질문 입력
   - AI의 맞춤형 답변 받기

### 종합 분석 사용법

1. **기본 정보 입력**
   - 나이, 연소득, 연지출, 저축액, 위험 성향 입력

2. **월별 지출 세부사항**
   - 주거비, 식비, 교통비, 공과금, 여가비, 기타 입력
   - 파이 차트로 지출 분포 시각화

### 포트폴리오 시뮬레이션 사용법

1. **포트폴리오 설정**
   - 종목 코드 입력 (야후 파이낸스 형식: 005930.KS)
   - 투자 기간 및 금액 설정
   - 위험 성향 선택

2. **시뮬레이션 실행**
   - 효율적 프론티어 생성
   - 최적 포트폴리오 구성 확인
   - 성과 지표 분석

### 투자 분석 사용법

1. **종목 분석**
   - 종목 코드 입력
   - 감정 분석 또는 시장 예측 선택

2. **결과 확인**
   - 감정 지수 게이지 차트
   - 시장 예측 결과 및 투자 권고사항

3. **현재 투자 현황**
   - 주식, 채권, 현금 보유량 입력

4. **분석 실행**
   - 상세 분석 또는 요약 분석 선택
   - 결과 확인 및 권장사항 검토

## 🏗️ 프로젝트 구조

```
AI-finance-advisor/
├── main.py                    # 메인 Streamlit 앱
├── requirements.txt           # Python 의존성
├── Dockerfile                 # Docker 설정
├── docker-compose.yml         # Docker Compose 설정
├── README.md                  # 프로젝트 문서
├── EXECUTION_GUIDE.md         # 실행 가이드
├── PERFORMANCE_OPTIMIZATION.md # 성능 최적화 가이드
├── SECURITY.md                # 보안 가이드
├── env_example.txt            # 환경변수 예제
├── src/                       # 소스 코드
│   ├── agents/               # AI 에이전트들
│   │   ├── base_agent.py     # 기본 에이전트
│   │   ├── budget_agent.py   # 예산 관리 에이전트
│   │   ├── investment_agent.py # 투자 자문 에이전트
│   │   ├── tax_agent.py      # 세금 절약 에이전트
│   │   ├── retirement_agent.py # 은퇴 계획 에이전트
│   │   └── multi_agent_system.py # 멀티 에이전트 시스템
│   ├── api/                  # FastAPI 백엔드
│   │   └── main.py           # API 메인 서버 (통합)
│   ├── core/                 # 핵심 기능
│   │   ├── config.py         # 설정 관리
│   │   ├── utils.py          # 유틸리티 함수
│   │   ├── financial_data.py # 실시간 재무 데이터
│   │   ├── portfolio_simulator.py # 포트폴리오 시뮬레이션
│   │   └── advanced_ai.py    # 고급 AI 기능
│   ├── rag/                  # RAG 시스템
│   │   ├── knowledge_base.py # 지식베이스
│   │   ├── vector_store.py   # 벡터 저장소
│   │   └── document_processor.py # 문서 처리
│   └── ui/                   # Streamlit UI (정리됨)
├── data/                     # 데이터 파일
│   ├── knowledge_base/       # 지식베이스 문서
│   ├── vector_db/           # 벡터 데이터베이스
│   ├── chroma_db/           # ChromaDB 데이터
│   └── user_data/           # 사용자 데이터
├── logs/                     # 로그 파일
└── 00_stop_all.bat          # 모든 서비스 중지
```

## 🔧 환경 설정

### 필수 환경변수

```bash
# Azure OpenAI 설정
AOAI_ENDPOINT=https://your-resource.openai.azure.com/
AOAI_API_KEY=your_azure_openai_api_key_here
AOAI_DEPLOY_EMBED_3_SMALL=text-embedding-3-small

# 애플리케이션 설정
APP_ENV=development
LOG_LEVEL=INFO
```

### Azure OpenAI 설정

1. Azure Portal에서 OpenAI 리소스 생성
2. 모델 배포 (GPT-4, text-embedding-3-small)
3. API 키 및 엔드포인트 복사
4. .env 파일에 설정 입력

## 📊 성능 최적화

- **캐싱 시스템**: Redis를 통한 응답 캐싱
- **비동기 처리**: FastAPI의 비동기 처리 활용
- **벡터 DB**: ChromaDB를 통한 효율적인 검색
- **로딩 상태**: 사용자 경험 개선을 위한 UI 최적화

## 🔒 보안

- **API 키 보안**: 환경변수를 통한 민감 정보 관리
- **입력 검증**: FastAPI의 Pydantic 모델 활용
- **CORS 설정**: 적절한 CORS 정책 적용
- **로깅**: 보안 이벤트 로깅

## 🤝 기여하기

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 🔧 문제 해결

### API 서버 연결 오류
회사 개발환경에서 API 서버가 작동하지 않는 경우:

1. **간단 버전 사용**: `start_simple.bat` 실행
   - API 서버 없이 내장 로직으로 동작
   - 최소 의존성으로 빠른 실행

2. **직접 실행 버전 사용**: `start_direct.bat` 실행
   - API 서버 없이 전체 기능 사용
   - LangChain과 Azure OpenAI 직접 사용

3. **포트 충돌 해결**:
   ```bash
   # 다른 포트 사용
   streamlit run main_simple.py --server.port 8503
   ```

### 의존성 설치 오류
```bash
# 최소 의존성만 설치
pip install streamlit pandas numpy plotly python-dotenv

# 전체 의존성 설치
pip install -r requirements.txt
```

### 환경변수 설정
`.env` 파일이 없는 경우:
```bash
# 기본 설정으로 실행 (간단 버전)
start_simple.bat
```

## 📝 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다. 자세한 내용은 `LICENSE` 파일을 참조하세요.

## 📞 지원

- **이슈 리포트**: GitHub Issues
- **문서**: `EXECUTION_GUIDE.md`, `PERFORMANCE_OPTIMIZATION.md`
- **보안**: `SECURITY.md`

## 🎉 감사의 말

- LangChain 팀
- Streamlit 팀
- FastAPI 팀
- Azure OpenAI 팀

---

**AI 재무관리 어드바이저** - 더 나은 재무 미래를 위한 AI 솔루션 💰
