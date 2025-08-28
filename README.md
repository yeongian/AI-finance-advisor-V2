# AI 재무관리 어드바이저

AI Bootcamp 과제: 나만의 AI Agent 개발하기  
개인 재무 관리를 위한 지능형 AI 어드바이저 시스템

## 프로젝트 개요

이 프로젝트는 LangChain, LangGraph, RAG(Retrieval-Augmented Generation) 기술을 활용하여 개발된 완전한 AI 재무관리 어드바이저입니다.
사용자의 재무 상황을 종합적으로 분석하고 맞춤형 조언을 제공하는 멀티 에이전트 시스템으로 구성되어 있습니다.

### 과제 평가 요소 충족

- **Prompt Engineering**: 최적화된 프롬프트 설계 및 Chain-of-Thought 적용
- **LangChain & LangGraph**: 멀티 에이전트 시스템 구현
- **RAG**: 금융 지식베이스 기반 검색 및 증강 생성
- **Streamlit**: 완성도 높은 웹 인터페이스
- **FastAPI**: RESTful API 백엔드
- **Docker**: 컨테이너화 및 배포 환경

## 주요 기능

### 1. AI 상담 시스템
- **자연어 대화**: 재무 관련 질문에 대한 자연스러운 대화
- **멀티 에이전트 협업**: 전문 영역별 AI 에이전트들의 협업
- **컨텍스트 인식**: 대화 히스토리 기반 연속성 있는 상담

### 2. 종합 재무 분석
- **예산 분석**: 수입/지출 패턴 분석 및 최적화 제안
- **투자 분석**: 포트폴리오 분석 및 투자 전략 수립
- **세금 분석**: 세금공제 최적화 및 절세 전략
- **은퇴 계획**: 은퇴 자금 설계 및 연금 상품 분석

### 3. 전문 에이전트
- **예산 관리 에이전트**: 50/30/20 법칙, 지출 최적화
- **투자 관리 에이전트**: 자산배분, 위험관리, 시장분석
- **세금 관리 에이전트**: 연말정산, 세금공제, 절세전략
- **은퇴 계획 에이전트**: 은퇴자금, 연금상품, 로드맵

### 4. RAG 기반 지식 시스템
- **금융 지식베이스**: 개인재무, 투자, 세금, 은퇴 관련 지식
- **벡터 검색**: FAISS/ChromaDB 기반 유사도 검색
- **지식 증강**: 검색된 정보를 바탕으로 한 정확한 답변

## 기술 아키텍처

```
┌─────────────────────────────────────────────────────────────┐
│                    Streamlit UI (8501)                      │
├─────────────────────────────────────────────────────────────┤
│                    FastAPI Backend (8000)                   │
├─────────────────────────────────────────────────────────────┤
│                Multi-Agent System (LangGraph)               │
│  ┌─────────────┬─────────────┬─────────────┬─────────────┐  │
│  │   Budget    │ Investment  │     Tax     │ Retirement  │  │
│  │   Agent     │   Agent     │   Agent     │   Agent     │  │
│  └─────────────┴─────────────┴─────────────┴─────────────┘  │
├─────────────────────────────────────────────────────────────┤
│                RAG Knowledge Base System                    │
│  ┌─────────────┬─────────────┬─────────────┬─────────────┐  │
│  │ Document    │   Vector    │ Knowledge   │  Financial  │  │
│  │ Processor   │   Store     │   Base      │   Tools     │  │
│  └─────────────┴─────────────┴─────────────┴─────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

## 설치 및 실행

### 1. 저장소 클론
```bash
git clone https://github.com/yeongian/AI-finance-advisor.git
cd AI-finance-advisor
```

### 2. 의존성 설치
```bash
pip install -r requirements.txt
```

### 3. 환경변수 설정
```bash
# 환경변수 파일 복사
cp env_example.txt .env

# .env 파일 편집하여 OpenAI API 키 설정
# OPENAI_API_KEY=your_actual_api_key_here
```

### 4. 애플리케이션 실행

#### 방법 1: 통합 실행 스크립트 (권장)
```bash
python run_app.py
```

#### 방법 2: 개별 실행
```bash
# API 서버 시작
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000

# 새 터미널에서 Streamlit UI 시작
streamlit run src/ui/streamlit_app.py --server.port 8501
```

#### 방법 3: Docker 실행
```bash
# API 서버만 실행
docker-compose up finance-advisor-api

# API 서버 + UI 함께 실행
docker-compose --profile ui up
```

### 5. 접속
- **Streamlit UI**: http://localhost:8501
- **FastAPI 문서**: http://localhost:8000/docs
- **API 서버**: http://localhost:8000

## 사용 방법

### 1. 사용자 정보 입력
사이드바에서 다음 정보를 입력하세요:
- **기본 정보**: 나이, 연소득, 연지출, 저축액, 위험성향
- **상세 지출**: 주거비, 식비, 교통비, 통신비, 여가비 등
- **투자 현황**: 주식, 채권, 현금 등 현재 투자 포트폴리오

### 2. AI 상담
- **샘플 질문** 버튼을 클릭하거나 직접 질문을 입력
- 예: "개인 재무 관리는 어떻게 해야 하나요?", "투자 포트폴리오를 어떻게 구성해야 하나요?"

### 3. 종합 분석
- **종합 분석 실행** 버튼을 클릭하여 전체 재무 상황 분석
- 예산, 투자, 세금, 은퇴 계획을 종합적으로 검토

### 4. 전문 분석
각 탭에서 특정 영역의 상세 분석을 확인할 수 있습니다:
- **예산 관리**: 지출 패턴 분석 및 절약 방안
- **투자 관리**: 포트폴리오 분석 및 투자 전략
- **세금 관리**: 세금공제 분석 및 절세 전략

## API 사용법

### 기본 쿼리
```bash
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "개인 재무 관리는 어떻게 해야 하나요?",
    "user_data": {
      "age": 30,
      "income": 50000000,
      "expenses": 30000000,
      "savings": 10000000
    }
  }'
```

### 종합 분석
```bash
curl -X POST "http://localhost:8000/comprehensive-analysis" \
  -H "Content-Type: application/json" \
  -d '{
    "user_data": {
      "age": 30,
      "income": 50000000,
      "expenses": 30000000,
      "savings": 10000000,
      "risk_tolerance": "moderate"
    }
  }'
```

## 프로젝트 구조

```
AI-finance-advisor/
├── src/
│   ├── agents/                 # AI 에이전트들
│   │   ├── base_agent.py      # 기본 에이전트 클래스
│   │   ├── budget_agent.py    # 예산 관리 에이전트
│   │   ├── investment_agent.py # 투자 관리 에이전트
│   │   ├── tax_agent.py       # 세금 관리 에이전트
│   │   ├── retirement_agent.py # 은퇴 계획 에이전트
│   │   └── multi_agent_system.py # 멀티 에이전트 시스템
│   ├── api/                   # FastAPI 백엔드
│   │   └── main.py           # API 서버
│   ├── core/                  # 핵심 기능
│   │   ├── config.py         # 설정 관리
│   │   └── utils.py          # 유틸리티 함수
│   ├── rag/                   # RAG 시스템
│   │   ├── knowledge_base.py # 지식베이스 관리
│   │   ├── vector_store.py   # 벡터 저장소
│   │   └── document_processor.py # 문서 처리
│   └── ui/                    # Streamlit UI
│       └── streamlit_app.py  # 웹 인터페이스
├── data/                      # 데이터 파일
│   ├── knowledge_base/        # 지식베이스 문서
│   ├── user_data/            # 사용자 데이터
│   ├── vector_db/            # 벡터 데이터베이스
│   └── chroma_db/            # ChromaDB 저장소
├── logs/                      # 로그 파일
├── requirements.txt           # Python 의존성
├── env_example.txt           # 환경변수 예제
├── run_app.py                # 실행 스크립트
├── Dockerfile                # Docker 설정
├── docker-compose.yml        # Docker Compose 설정
└── README.md                 # 프로젝트 문서
```

## 주요 기술 스택

### AI/ML
- **LangChain**: AI Agent 프레임워크
- **LangGraph**: 멀티 에이전트 플로우
- **OpenAI GPT-4**: 자연어 처리
- **RAG**: 지식 검색 및 증강

### 백엔드
- **FastAPI**: REST API 서버
- **Uvicorn**: ASGI 서버
- **Pydantic**: 데이터 검증

### 프론트엔드
- **Streamlit**: 웹 인터페이스
- **Plotly**: 데이터 시각화
- **Pandas**: 데이터 처리

### 데이터베이스
- **FAISS**: 벡터 검색
- **ChromaDB**: 벡터 데이터베이스
- **SQLite**: 로컬 데이터베이스

### 배포
- **Docker**: 컨테이너화
- **Docker Compose**: 멀티 서비스 배포

## 과제 평가 요소 상세

### 1. Prompt Engineering
- **역할 기반 프롬프트**: 각 에이전트별 전문 역할 정의
- **Chain-of-Thought**: 단계별 사고 과정을 통한 정확한 답변
- **Few-shot Prompting**: 예시를 통한 일관된 응답 생성
- **재사용성**: 다양한 입력 상황에서 일관된 응답

### 2. LangChain & LangGraph
- **멀티 에이전트 시스템**: 4개 전문 에이전트 협업
- **ReAct 패턴**: Tool 사용을 통한 실용적 답변
- **멀티턴 대화**: 대화 히스토리 기반 연속성
- **상태 관리**: AgentState를 통한 시스템 상태 추적

### 3. RAG (Retrieval-Augmented Generation)
- **지식베이스 구축**: 금융 관련 문서 수집 및 전처리
- **벡터 데이터베이스**: FAISS/ChromaDB 활용
- **유사도 검색**: 사용자 질의에 대한 관련 정보 검색
- **지식 증강**: 검색된 정보를 바탕으로 한 정확한 답변

### 4. 서비스 개발 및 패키징
- **Streamlit UI**: 직관적이고 완성도 높은 웹 인터페이스
- **FastAPI**: RESTful API 백엔드
- **Docker**: 컨테이너화 및 배포 환경
- **환경변수 관리**: API 키 등 민감 정보 보안

## 확장 가능성

### 비즈니스 확장
- **금융권 연계**: 은행, 증권사 API 연동
- **핀테크 서비스**: 개인자산관리, 투자자문
- **스타트업 서비스**: 재무관리 SaaS 플랫폼

### 기술 확장
- **실시간 데이터**: 주식, 환율, 경제지표 실시간 연동
- **머신러닝**: 사용자 행동 패턴 학습 및 예측
- **블록체인**: 투명한 재무 데이터 관리

## 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다.

## 기여

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 문의

프로젝트에 대한 문의사항이 있으시면 이슈를 생성해 주세요.

---

**AI 부트캠프 과제 - AI 재무관리 어드바이저**  
개발자: 현장경영팀 안영기 매니저  
기술 스택: LangChain, LangGraph, RAG, Streamlit, FastAPI, Docker
