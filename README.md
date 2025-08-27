# AI 개인 재무 관리 어드바이저 (Personal Finance AI Advisor)

## 📋 프로젝트 개요

이 프로젝트는 AI 기술을 활용하여 개인 재무 관리를 도와주는 지능형 어드바이저를 개발하는 것입니다. 사용자의 재무 상황을 분석하고 맞춤형 조언을 제공하여 더 나은 재무 계획을 수립할 수 있도록 도와줍니다.

## 🎯 주요 기능

### 1. 예산 분석 및 추천
- 소득/지출 패턴 분석
- 카테고리별 지출 분석
- 예산 최적화 제안

### 2. 투자 포트폴리오 최적화
- 위험도 기반 맞춤형 투자 조언
- 자산 배분 전략 제안
- 투자 상품 추천

### 3. 세금 절약 전략
- 연말정산 최적화 방안
- 세금공제 활용 전략
- 세무 상담

### 4. 부동산 투자 분석
- 지역별 시세 분석
- 수익률 계산
- 투자 적정성 평가

### 5. 은퇴 계획 수립
- 목표 기반 은퇴 자금 설계
- 연금 상품 분석
- 은퇴 준비 로드맵

## 🏗️ 기술 스택

### AI/ML
- **LangChain**: AI Agent 프레임워크
- **LangGraph**: 멀티 에이전트 플로우
- **OpenAI GPT**: 자연어 처리
- **RAG**: 지식 검색 및 증강

### 백엔드
- **FastAPI**: REST API 서버
- **SQLite**: 로컬 데이터베이스
- **FAISS/ChromaDB**: 벡터 데이터베이스

### 프론트엔드
- **Streamlit**: 웹 인터페이스
- **Plotly**: 데이터 시각화

### 데이터 처리
- **Pandas**: 데이터 분석
- **NumPy**: 수치 계산
- **yfinance**: 금융 데이터 수집

## 📁 프로젝트 구조

```
AI_Bootcamp/
├── main.py                 # 메인 실행 파일
├── requirements.txt        # 의존성 패키지
├── env_example.txt        # 환경변수 예제
├── README.md              # 프로젝트 설명서
├── src/                   # 소스 코드
│   ├── agents/           # AI 에이전트들
│   │   ├── budget_agent.py
│   │   ├── investment_agent.py
│   │   ├── tax_agent.py
│   │   └── retirement_agent.py
│   ├── core/             # 핵심 기능
│   │   ├── config.py
│   │   ├── database.py
│   │   └── utils.py
│   ├── data/             # 데이터 처리
│   │   ├── collectors/
│   │   └── processors/
│   ├── rag/              # RAG 시스템
│   │   ├── knowledge_base/
│   │   └── vector_store.py
│   └── ui/               # 사용자 인터페이스
│       ├── streamlit_app.py
│       └── components/
├── data/                 # 데이터 파일
│   ├── knowledge_base/   # 지식 베이스 문서
│   └── user_data/        # 사용자 데이터
├── logs/                 # 로그 파일
└── tests/                # 테스트 코드
```

## 🚀 설치 및 실행

### 1. 환경 설정
```bash
# 저장소 클론
git clone <repository-url>
cd AI_Bootcamp

# 가상환경 생성 및 활성화
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt
```

### 2. 환경변수 설정
```bash
# 환경변수 파일 복사
cp env_example.txt .env

# .env 파일을 편집하여 API 키 입력
# OPENAI_API_KEY=your_actual_api_key_here
```

### 3. 애플리케이션 실행
```bash
# Streamlit 앱 실행
streamlit run src/ui/streamlit_app.py

# FastAPI 서버 실행 (선택사항)
uvicorn src.api.main:app --reload
```

## 🔧 개발 가이드

### AI Agent 개발
1. **에이전트 설계**: 각 전문 영역별 에이전트 정의
2. **프롬프트 엔지니어링**: 역할 기반 프롬프트 최적화
3. **멀티 에이전트 플로우**: LangGraph를 활용한 에이전트 간 협업

### RAG 시스템 구축
1. **지식 베이스 구축**: 금융 관련 문서 수집 및 전처리
2. **벡터 데이터베이스**: FAISS/ChromaDB를 활용한 임베딩 저장
3. **검색 시스템**: 사용자 질의에 대한 관련 정보 검색

### UI/UX 개발
1. **Streamlit 인터페이스**: 직관적인 사용자 인터페이스
2. **데이터 시각화**: Plotly를 활용한 차트 및 그래프
3. **반응형 디자인**: 다양한 디바이스 지원

## 📊 평가 기준

### 기술적 요소
- ✅ **Prompt Engineering**: 최적화된 프롬프트 설계
- ✅ **LangChain & LangGraph**: 멀티 에이전트 구현
- ✅ **RAG**: 지식 검색 및 증강 시스템
- ✅ **Streamlit**: 사용자 인터페이스
- ✅ **FastAPI**: 백엔드 API (선택사항)
- ✅ **Docker**: 배포 환경 (선택사항)

### 비즈니스 가치
- 💼 **실용성**: 실제 재무 관리에 활용 가능
- 💼 **확장성**: 다양한 금융 서비스로 확장 가능
- 💼 **차별화**: 기존 서비스와 차별화된 기능

## 🤝 기여 방법

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 📝 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다.

## 📞 문의

프로젝트에 대한 문의사항이 있으시면 이슈를 생성해 주세요.
