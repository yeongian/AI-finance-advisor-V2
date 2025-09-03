# 🏗️ AI 재무관리 어드바이저 - 아키텍처 문서

## 📋 목차
1. [사용자 플로우 다이어그램](#사용자-플로우-다이어그램)
2. [서비스 아키텍처 다이어그램](#서비스-아키텍처-다이어그램)
3. [시스템 구성 요소](#시스템-구성-요소)
4. [데이터 플로우](#데이터-플로우)

---

## 🎯 사용자 플로우 다이어그램

```mermaid
flowchart TD
    A[사용자 접속] --> B{실행 모드 선택}
    
    B -->|간단 버전| C[main_simple.py 실행]
    B -->|직접 실행 버전| D[main_direct.py 실행]
    B -->|기존 API 서버| E[main.py + API 서버]
    
    C --> F[간단 모드 초기화]
    D --> G{전체 기능 모듈 로드}
    E --> H[API 서버 연결]
    
    G -->|성공| I[전체 기능 모드]
    G -->|실패| J[간단 모드 폴백]
    
    F --> K[메인 인터페이스]
    I --> K
    J --> K
    H --> K
    
    K --> L{기능 선택}
    
    L -->|재무 상담| M[상담 카테고리 선택]
    L -->|포트폴리오 분석| N[포트폴리오 데이터 입력]
    L -->|시장 데이터| O[주식 심볼 입력]
    
    M --> P[사용자 질문 입력]
    N --> Q[JSON 데이터 파싱]
    O --> R[시장 데이터 조회]
    
    P --> S{모드 확인}
    Q --> T[포트폴리오 분석]
    R --> U[데이터 처리]
    
    S -->|전체 기능| V[AI 에이전트 실행]
    S -->|간단 모드| W[내장 로직 실행]
    
    V --> X[RAG 지식 검색]
    W --> Y[키워드 기반 조언]
    
    X --> Z[AI 응답 생성]
    Y --> Z
    T --> AA[분석 결과 생성]
    U --> BB[차트 및 지표 생성]
    
    Z --> CC[결과 표시]
    AA --> CC
    BB --> CC
    
    CC --> DD[사용자 피드백]
    DD --> EE{추가 상담?}
    
    EE -->|예| L
    EE -->|아니오| FF[세션 종료]
    
    style A fill:#e1f5fe
    style K fill:#f3e5f5
    style CC fill:#e8f5e8
    style FF fill:#ffebee
```

### 🔄 사용자 플로우 설명

#### 1. **초기 접속 단계**
- 사용자가 Streamlit 실행 버튼 클릭
- 3가지 실행 모드 중 선택 (간단/직접/API 서버)

#### 2. **시스템 초기화 단계**
- **간단 버전**: 즉시 사용 가능한 내장 로직 로드
- **직접 실행**: 전체 기능 모듈 로드 시도 → 실패 시 간단 모드 폴백
- **API 서버**: FastAPI 서버 연결 및 상태 확인

#### 3. **기능 선택 단계**
- 재무 상담, 포트폴리오 분석, 시장 데이터 중 선택
- 각 기능별 맞춤형 입력 인터페이스 제공

#### 4. **데이터 처리 단계**
- **전체 기능 모드**: AI 에이전트 + RAG 지식 검색
- **간단 모드**: 키워드 기반 내장 로직
- **포트폴리오**: JSON 파싱 및 분석 알고리즘
- **시장 데이터**: 실시간/모의 데이터 처리

#### 5. **결과 표시 단계**
- 구조화된 응답, 차트, 지표를 통합 표시
- 사용자 피드백 수집 및 추가 상담 지원

---

## 🏛️ 서비스 아키텍처 다이어그램

```mermaid
graph TB
    subgraph "Frontend Layer"
        A[Streamlit UI]
        B[사용자 인터페이스]
        C[차트 및 시각화]
    end
    
    subgraph "Application Layer"
        D[DirectFinanceAdvisor]
        E[SimpleFinanceAdvisor]
        F[Multi Agent System]
    end
    
    subgraph "AI Layer"
        G[Azure OpenAI GPT-4o-mini]
        H[LangChain Framework]
        I[Embedding Model]
    end
    
    subgraph "Data Layer"
        J[RAG Knowledge Base]
        K[ChromaDB Vector Store]
        L[Financial Data APIs]
        M[Portfolio Simulator]
    end
    
    subgraph "Infrastructure Layer"
        N[Python Environment]
        O[Streamlit Server]
        P[File System]
        Q[Logging System]
    end
    
    subgraph "External Services"
        R[Alpha Vantage API]
        S[Yahoo Finance API]
        T[Azure OpenAI Service]
    end
    
    %% Frontend to Application
    A --> D
    A --> E
    B --> D
    B --> E
    C --> D
    C --> E
    
    %% Application to AI
    D --> F
    F --> G
    F --> H
    H --> I
    
    %% AI to Data
    H --> J
    I --> K
    F --> L
    F --> M
    
    %% Data to External
    L --> R
    L --> S
    G --> T
    I --> T
    
    %% Infrastructure connections
    D --> N
    E --> N
    A --> O
    J --> P
    D --> Q
    E --> Q
    
    %% Styling
    classDef frontend fill:#e3f2fd
    classDef application fill:#f3e5f5
    classDef ai fill:#e8f5e8
    classDef data fill:#fff3e0
    classDef infrastructure fill:#fce4ec
    classDef external fill:#f1f8e9
    
    class A,B,C frontend
    class D,E,F application
    class G,H,I ai
    class J,K,L,M data
    class N,O,P,Q infrastructure
    class R,S,T external
```

### 🏗️ 아키텍처 구성 요소

#### **Frontend Layer (프론트엔드 계층)**
- **Streamlit UI**: 사용자 인터페이스 및 상호작용
- **차트 및 시각화**: Plotly 기반 인터랙티브 차트
- **반응형 디자인**: 다양한 화면 크기에 대응

#### **Application Layer (애플리케이션 계층)**
- **DirectFinanceAdvisor**: 전체 기능 통합 관리자
- **SimpleFinanceAdvisor**: 간단 모드 전용 관리자
- **Multi Agent System**: 전문 에이전트들 (예산/투자/세무/퇴직)

#### **AI Layer (AI 계층)**
- **Azure OpenAI GPT-4o-mini**: 메인 LLM 모델
- **LangChain Framework**: AI 워크플로우 관리
- **Embedding Model**: 텍스트 벡터화 (text-embedding-3-small)

#### **Data Layer (데이터 계층)**
- **RAG Knowledge Base**: 금융 지식 문서 저장소
- **ChromaDB Vector Store**: 벡터 데이터베이스
- **Financial Data APIs**: 실시간 시장 데이터
- **Portfolio Simulator**: 포트폴리오 분석 엔진

#### **Infrastructure Layer (인프라 계층)**
- **Python Environment**: 실행 환경
- **Streamlit Server**: 웹 서버
- **File System**: 로그 및 데이터 저장
- **Logging System**: 시스템 모니터링

#### **External Services (외부 서비스)**
- **Alpha Vantage API**: 주식 시장 데이터
- **Yahoo Finance API**: 금융 정보
- **Azure OpenAI Service**: AI 모델 서비스

---

## 🔧 시스템 구성 요소

### **1. 핵심 모듈**
```
src/
├── agents/           # AI 에이전트 시스템
│   ├── budget_agent.py
│   ├── investment_agent.py
│   ├── tax_agent.py
│   ├── retirement_agent.py
│   └── multi_agent_system.py
├── core/            # 핵심 기능
│   ├── config.py
│   ├── financial_data.py
│   ├── portfolio_simulator.py
│   └── advanced_ai.py
├── rag/             # RAG 시스템
│   ├── knowledge_base.py
│   ├── document_processor.py
│   └── vector_store.py
└── api/             # API 서버
    └── main.py
```

### **2. 실행 파일**
```
├── main.py              # 기존 API 서버 방식
├── main_direct.py       # 직접 실행 버전
├── main_simple.py       # 간단 버전
├── start_direct.bat     # 직접 실행 배치
└── start_simple.bat     # 간단 실행 배치
```

---

## 📊 데이터 플로우

```mermaid
sequenceDiagram
    participant U as 사용자
    participant UI as Streamlit UI
    participant APP as Application Layer
    participant AI as AI Layer
    participant RAG as RAG System
    participant DB as Vector DB
    participant API as External APIs
    
    U->>UI: 재무 상담 요청
    UI->>APP: 사용자 입력 전달
    APP->>AI: 프롬프트 생성
    AI->>RAG: 관련 정보 검색 요청
    RAG->>DB: 벡터 검색
    DB-->>RAG: 관련 문서 반환
    RAG-->>AI: 컨텍스트 정보 제공
    AI->>API: Azure OpenAI 호출
    API-->>AI: AI 응답
    AI-->>APP: 처리된 응답
    APP-->>UI: 결과 데이터
    UI-->>U: 상담 결과 표시
    
    Note over U,API: 포트폴리오 분석 플로우
    U->>UI: 포트폴리오 데이터 입력
    UI->>APP: JSON 데이터 전달
    APP->>APP: 데이터 검증 및 파싱
    APP->>APP: 포트폴리오 분석 실행
    APP-->>UI: 분석 결과
    UI-->>U: 차트 및 지표 표시
    
    Note over U,API: 시장 데이터 플로우
    U->>UI: 주식 심볼 입력
    UI->>APP: 심볼 전달
    APP->>API: 시장 데이터 요청
    API-->>APP: 실시간 데이터
    APP->>APP: 데이터 처리 및 분석
    APP-->>UI: 차트 데이터
    UI-->>U: 주가 차트 표시
```

### 🔄 데이터 플로우 설명

#### **1. 재무 상담 플로우**
1. 사용자 질문 입력
2. 프롬프트 생성 및 RAG 검색
3. Azure OpenAI API 호출
4. 응답 처리 및 구조화
5. 결과 표시

#### **2. 포트폴리오 분석 플로우**
1. JSON 데이터 입력 및 검증
2. 자산 배분 계산
3. 리스크 평가
4. 시각화 데이터 생성
5. 차트 및 지표 표시

#### **3. 시장 데이터 플로우**
1. 주식 심볼 입력
2. 외부 API 호출 (실시간/모의)
3. 데이터 정제 및 분석
4. 차트 생성
5. 결과 표시

---

## 🎯 주요 특징

### **✅ 장점**
- **모듈화된 설계**: 각 기능이 독립적으로 개발 및 유지보수 가능
- **확장성**: 새로운 에이전트나 기능 추가 용이
- **호환성**: 다양한 환경에서 실행 가능
- **안정성**: 오류 발생 시 자동 폴백 메커니즘

### **🔧 기술적 특징**
- **하이브리드 아키텍처**: 전체 기능 + 간단 모드 이중 구조
- **RAG 통합**: 정확한 정보 제공을 위한 지식베이스 활용
- **실시간 처리**: 사용자 입력에 대한 즉시 응답
- **시각화**: 인터랙티브 차트 및 대시보드

이 아키텍처를 통해 사용자는 안정적이고 정확한 재무 상담 서비스를 24/7 이용할 수 있습니다.
