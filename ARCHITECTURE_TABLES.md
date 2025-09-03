# 📊 AI 재무관리 어드바이저 - 아키텍처 표 문서

## 📋 목차
1. [사용자 플로우 표](#사용자-플로우-표)
2. [서비스 아키텍처 구성표](#서비스-아키텍처-구성표)
3. [시스템 구성 요소 표](#시스템-구성-요소-표)
4. [데이터 플로우 표](#데이터-플로우-표)
5. [기능별 처리 방식 표](#기능별-처리-방식-표)

---

## 🎯 사용자 플로우 표

### **전체 사용자 경험 플로우**

| 단계 | 단계명 | 설명 | 세부 동작 | 결과물 |
|------|--------|------|-----------|--------|
| 1 | **초기 접속** | 사용자 시스템 접속 | Streamlit 실행 버튼 클릭 | 웹 인터페이스 로드 |
| 2 | **실행 모드 선택** | 3가지 실행 방식 중 선택 | 간단/직접/API 서버 모드 선택 | 실행 환경 결정 |
| 3 | **시스템 초기화** | 선택된 모드에 따른 초기화 | 모듈 로드 및 연결 확인 | 시스템 준비 완료 |
| 4 | **기능 선택** | 3가지 주요 기능 중 선택 | 재무상담/포트폴리오/시장데이터 | 기능별 인터페이스 |
| 5 | **데이터 입력** | 사용자 정보 입력 | 질문/JSON데이터/주식심볼 입력 | 처리 가능한 데이터 |
| 6 | **데이터 처리** | AI/알고리즘 처리 | AI에이전트/내장로직/분석알고리즘 | 처리된 결과 |
| 7 | **결과 생성** | 응답 및 시각화 생성 | AI응답/차트/지표 생성 | 완성된 결과물 |
| 8 | **결과 표시** | 사용자에게 결과 제공 | 구조화된 응답 및 차트 표시 | 사용자 피드백 |
| 9 | **피드백 처리** | 사용자 반응 확인 | 추가 상담 여부 확인 | 세션 지속/종료 |

### **실행 모드별 특징**

| 실행 모드 | 파일명 | 특징 | 장점 | 단점 | 접속 URL |
|-----------|--------|------|------|------|----------|
| **간단 버전** | `main_simple.py` | 내장 로직만 사용 | 안정적, 빠른 실행 | 기능 제한적 | `http://localhost:8502` |
| **직접 실행** | `main_direct.py` | 전체 기능 직접 통합 | 완전한 기능 | 의존성 문제 가능 | `http://localhost:8501` |
| **API 서버** | `main.py` | FastAPI 서버 연동 | 확장성, 분리된 구조 | 서버 연결 필요 | `http://localhost:8500` |

---

## 🏛️ 서비스 아키텍처 구성표

### **계층별 구성 요소**

| 계층 | 구성 요소 | 역할 | 기술 스택 | 의존성 |
|------|-----------|------|-----------|--------|
| **Frontend Layer** | Streamlit UI | 사용자 인터페이스 | Streamlit, Plotly | Application Layer |
| | 사용자 인터페이스 | 상호작용 처리 | HTML/CSS/JS | - |
| | 차트 및 시각화 | 데이터 시각화 | Plotly, Matplotlib | - |
| **Application Layer** | DirectFinanceAdvisor | 전체 기능 관리자 | Python, LangChain | AI Layer, Data Layer |
| | SimpleFinanceAdvisor | 간단 모드 관리자 | Python | - |
| | Multi Agent System | 전문 에이전트 시스템 | LangChain, LangGraph | AI Layer |
| **AI Layer** | Azure OpenAI GPT-4o-mini | 메인 LLM 모델 | Azure OpenAI API | External Services |
| | LangChain Framework | AI 워크플로우 관리 | LangChain | - |
| | Embedding Model | 텍스트 벡터화 | text-embedding-3-small | External Services |
| **Data Layer** | RAG Knowledge Base | 금융 지식 저장소 | ChromaDB | Infrastructure Layer |
| | ChromaDB Vector Store | 벡터 데이터베이스 | ChromaDB | - |
| | Financial Data APIs | 시장 데이터 수집 | Alpha Vantage, Yahoo Finance | External Services |
| | Portfolio Simulator | 포트폴리오 분석 엔진 | Python, NumPy, Pandas | - |
| **Infrastructure Layer** | Python Environment | 실행 환경 | Python 3.8+ | - |
| | Streamlit Server | 웹 서버 | Streamlit | - |
| | File System | 데이터 저장 | OS File System | - |
| | Logging System | 시스템 모니터링 | Python Logging | - |
| **External Services** | Alpha Vantage API | 주식 시장 데이터 | REST API | - |
| | Yahoo Finance API | 금융 정보 | REST API | - |
| | Azure OpenAI Service | AI 모델 서비스 | Azure Cloud | - |

### **계층간 연결 관계**

| 출발 계층 | 도착 계층 | 연결 방식 | 데이터 타입 | 설명 |
|-----------|-----------|-----------|-------------|------|
| Frontend | Application | HTTP/WebSocket | JSON | 사용자 입력 및 결과 |
| Application | AI | Direct Import | Python Objects | AI 모델 호출 |
| AI | Data | Direct Import | Python Objects | 지식 검색 및 데이터 요청 |
| Data | External Services | HTTP API | JSON/REST | 외부 데이터 수집 |
| Application | Infrastructure | Direct Import | Python Objects | 로깅 및 파일 저장 |

---

## 🔧 시스템 구성 요소 표

### **핵심 모듈 구조**

| 디렉토리 | 파일명 | 역할 | 주요 클래스/함수 | 의존성 |
|----------|--------|------|------------------|--------|
| `src/agents/` | `budget_agent.py` | 예산 관리 에이전트 | BudgetAnalysisTool | LangChain |
| | `investment_agent.py` | 투자 상담 에이전트 | InvestmentAnalysisTool | LangChain |
| | `tax_agent.py` | 세무 상담 에이전트 | TaxPlanningTool | LangChain |
| | `retirement_agent.py` | 퇴직 계획 에이전트 | RetirementPlanningTool | LangChain |
| | `multi_agent_system.py` | 다중 에이전트 시스템 | MultiAgentSystem | 모든 에이전트 |
| `src/core/` | `config.py` | 설정 관리 | Config | - |
| | `financial_data.py` | 금융 데이터 처리 | FinancialData | External APIs |
| | `portfolio_simulator.py` | 포트폴리오 분석 | PortfolioSimulator | NumPy, Pandas |
| | `advanced_ai.py` | 고급 AI 기능 | AdvancedAI | Azure OpenAI |
| `src/rag/` | `knowledge_base.py` | 지식베이스 관리 | KnowledgeBase | ChromaDB |
| | `document_processor.py` | 문서 처리 | DocumentProcessor | - |
| | `vector_store.py` | 벡터 저장소 | VectorStore | ChromaDB |
| `src/api/` | `main.py` | FastAPI 서버 | FastAPI App | FastAPI, Uvicorn |

### **실행 파일 구성**

| 파일명 | 실행 방식 | 주요 기능 | 의존성 | 포트 |
|--------|-----------|-----------|--------|------|
| `main.py` | API 서버 방식 | 전체 기능 (API 기반) | FastAPI, Uvicorn | 8500 |
| `main_direct.py` | 직접 실행 방식 | 전체 기능 (직접 통합) | 모든 모듈 | 8501 |
| `main_simple.py` | 간단 실행 방식 | 기본 기능 (내장 로직) | 최소 의존성 | 8502 |
| `start_direct.bat` | 배치 실행 | 직접 실행 자동화 | Windows Batch | - |
| `start_simple.bat` | 배치 실행 | 간단 실행 자동화 | Windows Batch | - |

---

## 📊 데이터 플로우 표

### **재무 상담 데이터 플로우**

| 단계 | 처리 주체 | 입력 데이터 | 처리 방식 | 출력 데이터 | 다음 단계 |
|------|-----------|-------------|-----------|-------------|-----------|
| 1 | 사용자 | 질문 텍스트 | 직접 입력 | 사용자 질문 | UI 전달 |
| 2 | Streamlit UI | 사용자 질문 | 데이터 검증 | 검증된 질문 | Application |
| 3 | Application | 검증된 질문 | 프롬프트 생성 | 구조화된 프롬프트 | AI Layer |
| 4 | AI Layer | 구조화된 프롬프트 | RAG 검색 요청 | 검색 쿼리 | RAG System |
| 5 | RAG System | 검색 쿼리 | 벡터 검색 | 관련 문서 | AI Layer |
| 6 | AI Layer | 관련 문서 | Azure OpenAI 호출 | AI 응답 | Application |
| 7 | Application | AI 응답 | 응답 처리 및 구조화 | 처리된 응답 | UI |
| 8 | Streamlit UI | 처리된 응답 | 결과 표시 | 사용자 결과 | 사용자 |

### **포트폴리오 분석 데이터 플로우**

| 단계 | 처리 주체 | 입력 데이터 | 처리 방식 | 출력 데이터 | 다음 단계 |
|------|-----------|-------------|-----------|-------------|-----------|
| 1 | 사용자 | JSON 포트폴리오 데이터 | 직접 입력 | 원시 JSON | UI 전달 |
| 2 | Streamlit UI | 원시 JSON | JSON 파싱 | 파싱된 데이터 | Application |
| 3 | Application | 파싱된 데이터 | 데이터 검증 | 검증된 데이터 | 분석 엔진 |
| 4 | Portfolio Simulator | 검증된 데이터 | 자산 배분 계산 | 배분 결과 | Application |
| 5 | Portfolio Simulator | 배분 결과 | 리스크 평가 | 리스크 지표 | Application |
| 6 | Application | 분석 결과 | 시각화 데이터 생성 | 차트 데이터 | UI |
| 7 | Streamlit UI | 차트 데이터 | Plotly 차트 생성 | 인터랙티브 차트 | 사용자 |

### **시장 데이터 플로우**

| 단계 | 처리 주체 | 입력 데이터 | 처리 방식 | 출력 데이터 | 다음 단계 |
|------|-----------|-------------|-----------|-------------|-----------|
| 1 | 사용자 | 주식 심볼 | 직접 입력 | 심볼 텍스트 | UI 전달 |
| 2 | Streamlit UI | 심볼 텍스트 | 데이터 검증 | 검증된 심볼 | Application |
| 3 | Application | 검증된 심볼 | API 호출 요청 | API 요청 | External API |
| 4 | External API | API 요청 | 실시간 데이터 조회 | 원시 시장 데이터 | Application |
| 5 | Application | 원시 시장 데이터 | 데이터 정제 및 분석 | 처리된 데이터 | UI |
| 6 | Streamlit UI | 처리된 데이터 | 차트 생성 | 주가 차트 | 사용자 |

---

## 🎯 기능별 처리 방식 표

### **모드별 기능 처리 방식**

| 기능 | 전체 기능 모드 | 간단 모드 | API 서버 모드 |
|------|----------------|-----------|---------------|
| **재무 상담** | AI 에이전트 + RAG | 키워드 기반 내장 로직 | API 호출 + AI 에이전트 |
| **포트폴리오 분석** | 고급 분석 알고리즘 | 기본 계산 로직 | API 호출 + 고급 분석 |
| **시장 데이터** | 실시간 API + 고급 차트 | 모의 데이터 + 기본 차트 | API 호출 + 실시간 데이터 |
| **응답 품질** | 높음 (AI 기반) | 보통 (규칙 기반) | 높음 (AI 기반) |
| **처리 속도** | 보통 (AI 처리 시간) | 빠름 (즉시 처리) | 보통 (네트워크 지연) |
| **안정성** | 중간 (의존성 문제 가능) | 높음 (독립적 실행) | 중간 (서버 연결 필요) |

### **에이전트별 전문 분야**

| 에이전트 | 전문 분야 | 주요 기능 | 입력 데이터 | 출력 결과 |
|----------|-----------|-----------|-------------|-----------|
| **Budget Agent** | 예산 관리 | 지출 분석, 예산 계획 | 수입/지출 데이터 | 예산 권장사항 |
| **Investment Agent** | 투자 상담 | 포트폴리오 구성, 리스크 관리 | 투자 목표, 위험 성향 | 투자 전략 |
| **Tax Agent** | 세무 계획 | 세금 절약, 세무 최적화 | 소득, 지출 정보 | 세무 계획 |
| **Retirement Agent** | 퇴직 계획 | 퇴직 준비, 연금 계획 | 나이, 소득, 목표 | 퇴직 전략 |

### **기술 스택별 역할**

| 기술 스택 | 역할 | 사용 위치 | 주요 기능 | 버전 |
|-----------|------|-----------|-----------|------|
| **Streamlit** | 웹 프레임워크 | Frontend Layer | UI 구성, 상호작용 | 1.28+ |
| **LangChain** | AI 프레임워크 | AI Layer | 에이전트 관리, 워크플로우 | 0.1+ |
| **Azure OpenAI** | LLM 서비스 | AI Layer | 텍스트 생성, 분석 | GPT-4o-mini |
| **ChromaDB** | 벡터 데이터베이스 | Data Layer | 문서 검색, 벡터 저장 | 0.4+ |
| **Plotly** | 시각화 라이브러리 | Frontend Layer | 인터랙티브 차트 | 5.15+ |
| **FastAPI** | API 프레임워크 | API Layer | REST API 서버 | 0.104+ |
| **Pandas** | 데이터 처리 | Data Layer | 데이터 분석, 조작 | 2.0+ |
| **NumPy** | 수치 계산 | Data Layer | 수학적 연산 | 1.24+ |

---

## 🎯 주요 특징 요약

### **✅ 시스템 장점**

| 특징 | 설명 | 효과 |
|------|------|------|
| **모듈화된 설계** | 각 기능이 독립적으로 개발 및 유지보수 가능 | 개발 효율성 향상 |
| **확장성** | 새로운 에이전트나 기능 추가 용이 | 시스템 성장 가능 |
| **호환성** | 다양한 환경에서 실행 가능 | 배포 유연성 |
| **안정성** | 오류 발생 시 자동 폴백 메커니즘 | 서비스 연속성 |

### **🔧 기술적 특징**

| 특징 | 설명 | 구현 방식 |
|------|------|-----------|
| **하이브리드 아키텍처** | 전체 기능 + 간단 모드 이중 구조 | 자동 폴백 시스템 |
| **RAG 통합** | 정확한 정보 제공을 위한 지식베이스 활용 | ChromaDB + Embedding |
| **실시간 처리** | 사용자 입력에 대한 즉시 응답 | Streamlit + AI 모델 |
| **시각화** | 인터랙티브 차트 및 대시보드 | Plotly + Streamlit |

이 표 문서를 통해 AI 재무관리 어드바이저의 전체 구조와 동작 방식을 체계적으로 이해할 수 있습니다.
