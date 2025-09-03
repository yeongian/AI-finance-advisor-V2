# 🏗️ AI 재무관리 어드바이저 - 아키텍처 다이어그램 문서

## 📋 목차
1. [사용자 플로우 다이어그램](#사용자-플로우-다이어그램)
2. [서비스 아키텍처 다이어그램](#서비스-아키텍처-다이어그램)
3. [시스템 구성 요소 다이어그램](#시스템-구성-요소-다이어그램)
4. [데이터 플로우 다이어그램](#데이터-플로우-다이어그램)
5. [기능별 처리 방식 다이어그램](#기능별-처리-방식-다이어그램)

---

## 🎯 사용자 플로우 다이어그램

### **전체 사용자 경험 플로우**

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

### **실행 모드별 특징 비교**

```mermaid
graph LR
    subgraph "실행 모드 비교"
        A[간단 버전<br/>main_simple.py<br/>내장 로직만 사용<br/>안정적, 빠른 실행<br/>기능 제한적<br/>localhost:8502]
        B[직접 실행<br/>main_direct.py<br/>전체 기능 직접 통합<br/>완전한 기능<br/>의존성 문제 가능<br/>localhost:8501]
        C[API 서버<br/>main.py<br/>FastAPI 서버 연동<br/>확장성, 분리된 구조<br/>서버 연결 필요<br/>localhost:8500]
    end
    
    style A fill:#e8f5e8
    style B fill:#fff3e0
    style C fill:#f3e5f5
```

---

## 🏛️ 서비스 아키텍처 다이어그램

### **전체 시스템 아키텍처**

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

### **계층간 데이터 흐름**

```mermaid
flowchart LR
    subgraph "데이터 흐름"
        A[Frontend Layer] -->|JSON/HTTP| B[Application Layer]
        B -->|Python Objects| C[AI Layer]
        C -->|Search Queries| D[Data Layer]
        D -->|HTTP API| E[External Services]
        B -->|Log Data| F[Infrastructure Layer]
    end
    
    style A fill:#e3f2fd
    style B fill:#f3e5f5
    style C fill:#e8f5e8
    style D fill:#fff3e0
    style E fill:#f1f8e9
    style F fill:#fce4ec
```

---

## 🔧 시스템 구성 요소 다이어그램

### **핵심 모듈 구조**

```mermaid
graph TD
    subgraph "src/agents/"
        A1[budget_agent.py<br/>예산 관리 에이전트]
        A2[investment_agent.py<br/>투자 상담 에이전트]
        A3[tax_agent.py<br/>세무 상담 에이전트]
        A4[retirement_agent.py<br/>퇴직 계획 에이전트]
        A5[multi_agent_system.py<br/>다중 에이전트 시스템]
    end
    
    subgraph "src/core/"
        B1[config.py<br/>설정 관리]
        B2[financial_data.py<br/>금융 데이터 처리]
        B3[portfolio_simulator.py<br/>포트폴리오 분석]
        B4[advanced_ai.py<br/>고급 AI 기능]
    end
    
    subgraph "src/rag/"
        C1[knowledge_base.py<br/>지식베이스 관리]
        C2[document_processor.py<br/>문서 처리]
        C3[vector_store.py<br/>벡터 저장소]
    end
    
    subgraph "src/api/"
        D1[main.py<br/>FastAPI 서버]
    end
    
    A5 --> A1
    A5 --> A2
    A5 --> A3
    A5 --> A4
    
    style A1 fill:#e8f5e8
    style A2 fill:#e8f5e8
    style A3 fill:#e8f5e8
    style A4 fill:#e8f5e8
    style A5 fill:#f3e5f5
    style B1 fill:#fff3e0
    style B2 fill:#fff3e0
    style B3 fill:#fff3e0
    style B4 fill:#fff3e0
    style C1 fill:#e3f2fd
    style C2 fill:#e3f2fd
    style C3 fill:#e3f2fd
    style D1 fill:#fce4ec
```

### **실행 파일 구성**

```mermaid
graph LR
    subgraph "실행 파일"
        A[main.py<br/>API 서버 방식<br/>포트: 8500]
        B[main_direct.py<br/>직접 실행 방식<br/>포트: 8501]
        C[main_simple.py<br/>간단 실행 방식<br/>포트: 8502]
        D[start_direct.bat<br/>직접 실행 자동화]
        E[start_simple.bat<br/>간단 실행 자동화]
    end
    
    D --> B
    E --> C
    
    style A fill:#f3e5f5
    style B fill:#fff3e0
    style C fill:#e8f5e8
    style D fill:#fce4ec
    style E fill:#fce4ec
```

---

## 📊 데이터 플로우 다이어그램

### **재무 상담 데이터 플로우**

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
```

### **포트폴리오 분석 데이터 플로우**

```mermaid
flowchart TD
    A[사용자 JSON 입력] --> B[Streamlit UI 파싱]
    B --> C[데이터 검증]
    C --> D[Portfolio Simulator]
    D --> E[자산 배분 계산]
    E --> F[리스크 평가]
    F --> G[분석 결과 생성]
    G --> H[시각화 데이터 생성]
    H --> I[Plotly 차트 생성]
    I --> J[사용자 결과 표시]
    
    style A fill:#e1f5fe
    style D fill:#e8f5e8
    style J fill:#e8f5e8
```

### **시장 데이터 플로우**

```mermaid
flowchart LR
    A[주식 심볼 입력] --> B[데이터 검증]
    B --> C[API 호출 요청]
    C --> D[External API]
    D --> E[실시간 데이터 조회]
    E --> F[데이터 정제 및 분석]
    F --> G[차트 생성]
    G --> H[주가 차트 표시]
    
    style A fill:#e1f5fe
    style D fill:#f1f8e9
    style H fill:#e8f5e8
```

---

## 🎯 기능별 처리 방식 다이어그램

### **모드별 기능 처리 방식**

```mermaid
graph TB
    subgraph "전체 기능 모드"
        A1[AI 에이전트 + RAG<br/>고급 분석 알고리즘<br/>실시간 API + 고급 차트<br/>높은 응답 품질<br/>보통 처리 속도<br/>중간 안정성]
    end
    
    subgraph "간단 모드"
        A2[키워드 기반 내장 로직<br/>기본 계산 로직<br/>모의 데이터 + 기본 차트<br/>보통 응답 품질<br/>빠른 처리 속도<br/>높은 안정성]
    end
    
    subgraph "API 서버 모드"
        A3[API 호출 + AI 에이전트<br/>API 호출 + 고급 분석<br/>API 호출 + 실시간 데이터<br/>높은 응답 품질<br/>보통 처리 속도<br/>중간 안정성]
    end
    
    style A1 fill:#e8f5e8
    style A2 fill:#fff3e0
    style A3 fill:#f3e5f5
```

### **에이전트별 전문 분야**

```mermaid
graph LR
    subgraph "AI 에이전트 시스템"
        A[Budget Agent<br/>예산 관리<br/>지출 분석, 예산 계획]
        B[Investment Agent<br/>투자 상담<br/>포트폴리오 구성, 리스크 관리]
        C[Tax Agent<br/>세무 계획<br/>세금 절약, 세무 최적화]
        D[Retirement Agent<br/>퇴직 계획<br/>퇴직 준비, 연금 계획]
    end
    
    style A fill:#e8f5e8
    style B fill:#fff3e0
    style C fill:#f3e5f5
    style D fill:#e3f2fd
```

### **기술 스택별 역할**

```mermaid
graph TB
    subgraph "Frontend Technologies"
        A[Streamlit<br/>웹 프레임워크<br/>UI 구성, 상호작용]
        B[Plotly<br/>시각화 라이브러리<br/>인터랙티브 차트]
    end
    
    subgraph "AI Technologies"
        C[LangChain<br/>AI 프레임워크<br/>에이전트 관리, 워크플로우]
        D[Azure OpenAI<br/>LLM 서비스<br/>텍스트 생성, 분석]
        E[ChromaDB<br/>벡터 데이터베이스<br/>문서 검색, 벡터 저장]
    end
    
    subgraph "Backend Technologies"
        F[FastAPI<br/>API 프레임워크<br/>REST API 서버]
        G[Pandas<br/>데이터 처리<br/>데이터 분석, 조작]
        H[NumPy<br/>수치 계산<br/>수학적 연산]
    end
    
    style A fill:#e3f2fd
    style B fill:#e3f2fd
    style C fill:#e8f5e8
    style D fill:#e8f5e8
    style E fill:#e8f5e8
    style F fill:#f3e5f5
    style G fill:#fff3e0
    style H fill:#fff3e0
```

---

## 🎯 주요 특징 다이어그램

### **시스템 장점**

```mermaid
mindmap
  root((AI 재무관리 어드바이저))
    모듈화된 설계
      독립적 개발
      유지보수 용이
      개발 효율성 향상
    확장성
      새로운 에이전트 추가
      기능 확장 용이
      시스템 성장 가능
    호환성
      다양한 환경 실행
      배포 유연성
      크로스 플랫폼
    안정성
      자동 폴백 메커니즘
      오류 처리
      서비스 연속성
```

### **기술적 특징**

```mermaid
graph LR
    subgraph "핵심 기술적 특징"
        A[하이브리드 아키텍처<br/>전체 기능 + 간단 모드<br/>자동 폴백 시스템]
        B[RAG 통합<br/>정확한 정보 제공<br/>ChromaDB + Embedding]
        C[실시간 처리<br/>즉시 응답<br/>Streamlit + AI 모델]
        D[시각화<br/>인터랙티브 차트<br/>Plotly + Streamlit]
    end
    
    style A fill:#e8f5e8
    style B fill:#fff3e0
    style C fill:#f3e5f5
    style D fill:#e3f2fd
```

---

## 📋 요약 표

### **실행 모드별 특징**

| 실행 모드 | 파일명 | 특징 | 장점 | 단점 | 접속 URL |
|-----------|--------|------|------|------|----------|
| **간단 버전** | `main_simple.py` | 내장 로직만 사용 | 안정적, 빠른 실행 | 기능 제한적 | `http://localhost:8502` |
| **직접 실행** | `main_direct.py` | 전체 기능 직접 통합 | 완전한 기능 | 의존성 문제 가능 | `http://localhost:8501` |
| **API 서버** | `main.py` | FastAPI 서버 연동 | 확장성, 분리된 구조 | 서버 연결 필요 | `http://localhost:8500` |

### **에이전트별 전문 분야**

| 에이전트 | 전문 분야 | 주요 기능 | 입력 데이터 | 출력 결과 |
|----------|-----------|-----------|-------------|-----------|
| **Budget Agent** | 예산 관리 | 지출 분석, 예산 계획 | 수입/지출 데이터 | 예산 권장사항 |
| **Investment Agent** | 투자 상담 | 포트폴리오 구성, 리스크 관리 | 투자 목표, 위험 성향 | 투자 전략 |
| **Tax Agent** | 세무 계획 | 세금 절약, 세무 최적화 | 소득, 지출 정보 | 세무 계획 |
| **Retirement Agent** | 퇴직 계획 | 퇴직 준비, 연금 계획 | 나이, 소득, 목표 | 퇴직 전략 |

이 다이어그램 문서를 통해 AI 재무관리 어드바이저의 전체 구조와 동작 방식을 시각적으로 이해할 수 있습니다.
