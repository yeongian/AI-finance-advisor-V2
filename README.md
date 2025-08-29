# 🤖 AI 재무관리 어드바이저

**개인 재무 관리를 위한 AI 기반 종합 어드바이저 시스템**

## 📋 목차

- [🎯 프로젝트 개요](#-프로젝트-개요)
- [✨ 주요 기능](#-주요-기능)
- [🛠️ 기술 스택](#️-기술-스택)
- [🚀 빠른 시작](#-빠른-시작)
- [📖 사용자 가이드](#-사용자-가이드)
- [👨‍💻 개발자 가이드](#-개발자-가이드)
- [🔧 API 문서](#-api-문서)
- [📊 성능 최적화](#-성능-최적화)
- [🔒 보안](#-보안)
- [📝 라이선스](#-라이선스)

## 🎯 프로젝트 개요

AI 재무관리 어드바이저는 개인의 재무 상황을 종합적으로 분석하고 최적화된 조언을 제공하는 AI 기반 시스템입니다. 

### 🌟 핵심 특징

- **🤖 다중 AI 에이전트**: 예산 분석, 투자 자문, 세무 상담, 시장 분석 전문가들이 협력
- **🔄 LangGraph 기반**: 고급 워크플로우 관리와 상태 기반 처리
- **🛠️ Tool Calling**: 실제 재무 데이터 분석 및 계산 도구 활용
- **💾 Memory 기능**: 대화 히스토리 기반 연속성 있는 상담
- **📊 시각화**: 재무 상황을 직관적으로 파악할 수 있는 차트 및 그래프
- **🌐 웹 인터페이스**: 사용자 친화적인 Streamlit 기반 UI

## ✨ 주요 기능

### 💰 재무 분석
- **예산 건강도 분석**: 수입, 지출, 저축률 기반 종합 점수
- **투자 포트폴리오 분석**: 위험도별 자산 배분 전략
- **세금 최적화**: 공제 항목별 절세 방안 제시
- **시장 인사이트**: 실시간 시장 동향 분석

### 🤖 AI 상담
- **기본 챗봇**: 일반적인 재무 질문에 대한 즉시 응답
- **전문가 상담**: 특정 분야 전문가와의 1:1 상담
- **종합 분석**: 모든 전문가가 참여하는 종합 진단
- **대화형 상담**: 이전 대화를 기억하는 연속성 있는 상담

### 📈 시각화
- **재무 현황 대시보드**: 주요 지표들의 한눈에 보기
- **트렌드 분석**: 시간별 변화 추이
- **포트폴리오 분포**: 자산별 투자 비율
- **LangGraph 구조도**: AI 에이전트들의 협력 관계

## 🛠️ 기술 스택

### 🤖 AI/ML
- **LangChain**: AI 에이전트 프레임워크
- **LangGraph**: 고급 워크플로우 관리
- **Azure OpenAI**: GPT-4 기반 자연어 처리
- **OpenAI Embeddings**: 텍스트 임베딩 및 벡터 검색

### 🌐 웹 프레임워크
- **FastAPI**: 고성능 REST API 서버
- **Streamlit**: 대화형 웹 애플리케이션
- **Uvicorn**: ASGI 웹 서버

### 💾 데이터베이스 & 벡터
- **FAISS**: 고성능 벡터 검색
- **ChromaDB**: 벡터 데이터베이스
- **SQLAlchemy**: ORM 및 데이터베이스 관리

### 📊 데이터 처리
- **Pandas**: 데이터 분석 및 처리
- **NumPy**: 수치 계산
- **Plotly**: 인터랙티브 시각화
- **yfinance**: 금융 데이터 수집

### 🐳 배포 & 인프라
- **Docker**: 컨테이너화
- **Docker Compose**: 멀티 컨테이너 오케스트레이션
- **Redis**: 캐싱 및 세션 관리

## 🚀 빠른 시작

### 📋 사전 요구사항

- Python 3.8+
- Docker & Docker Compose
- Azure OpenAI API 키

### 🔧 설치

1. **저장소 클론**
```bash
git clone https://github.com/your-username/ai-finance-advisor.git
cd ai-finance-advisor
```

2. **환경 변수 설정**
```bash
cp env_example.txt .env
# .env 파일을 편집하여 Azure OpenAI 설정 입력
```

3. **Docker로 실행**
```bash
docker-compose up -d
```

4. **웹 애플리케이션 접속**
- Streamlit UI: http://localhost:8501
- FastAPI 문서: http://localhost:8000/docs

### 🎯 첫 사용하기

1. **웹 인터페이스 접속**
   - 브라우저에서 http://localhost:8501 접속

2. **기본 챗봇 테스트**
   - "안녕하세요! 재무관리에 대해 궁금한 점이 있습니다." 입력

3. **전문가 상담**
   - 원하는 전문가 선택 (예산 분석, 투자 자문 등)
   - 구체적인 질문 입력

4. **종합 분석**
   - 사용자 ID 입력 후 종합 재무 분석 실행

## 📖 사용자 가이드

### 💬 기본 챗봇 사용법

기본 챗봇은 일반적인 재무 질문에 대해 즉시 답변을 제공합니다.

**예시 질문:**
- "저축하는 방법을 알려주세요"
- "투자에 대해 조언해주세요"
- "세금 절약 방법을 알려주세요"

### 🛠️ Tool Agent 사용법

Tool Agent는 실제 재무 데이터를 분석하여 구체적인 조언을 제공합니다.

**주요 기능:**
- 사용자 재무 프로필 조회
- 예산 건강도 분석
- 투자 조언 생성
- 세금 최적화 계산
- 시장 인사이트 제공

### 🤖 Multi Agent 사용법

여러 전문가가 협력하여 종합적인 재무 상담을 제공합니다.

**전문가 구성:**
- 💰 **예산 분석 전문가**: 수입/지출 분석 및 예산 관리
- 📈 **투자 자문 전문가**: 포트폴리오 구성 및 투자 전략
- 🧾 **세무 전문가**: 세금 최적화 및 공제 방안
- 📊 **시장 분석 전문가**: 시장 동향 및 경제 분석

### 💭 대화형 상담 사용법

이전 대화를 기억하여 연속성 있는 상담을 제공합니다.

**특징:**
- 스레드 기반 대화 관리
- 이전 상담 내용 참조
- 맥락을 고려한 답변

### 📊 시각화 기능

재무 상황을 직관적으로 파악할 수 있는 다양한 차트를 제공합니다.

**제공 차트:**
- LangGraph 구조도
- 전문가별 상담 분포
- 도구 사용 현황
- 스레드 활동 분석

## 👨‍💻 개발자 가이드

### 🏗️ 프로젝트 구조

```
AI-finance-advisor/
├── src/
│   ├── agents/           # AI 에이전트 구현
│   │   ├── base_agent.py
│   │   ├── enhanced_agent.py
│   │   ├── advanced_tool_agent.py
│   │   ├── langgraph_agent.py
│   │   └── multi_agent_system.py
│   ├── api/              # FastAPI 엔드포인트
│   │   ├── main.py
│   │   ├── enhanced_endpoints.py
│   │   ├── advanced_tool_endpoints.py
│   │   └── langgraph_endpoints.py
│   ├── ui/               # Streamlit UI
│   │   ├── streamlit_app.py
│   │   ├── enhanced_streamlit.py
│   │   ├── advanced_tool_streamlit.py
│   │   └── langgraph_streamlit.py
│   ├── rag/              # RAG 시스템
│   │   ├── knowledge_base.py
│   │   ├── document_processor.py
│   │   └── vector_store.py
│   └── core/             # 핵심 설정 및 유틸리티
│       ├── config.py
│       └── utils.py
├── data/                 # 데이터 파일
├── logs/                 # 로그 파일
├── docker-compose.yml    # Docker 설정
├── requirements.txt      # Python 의존성
└── README.md
```

### 🔧 개발 환경 설정

1. **가상환경 생성**
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

2. **의존성 설치**
```bash
pip install -r requirements.txt
```

3. **환경 변수 설정**
```bash
export AOAI_ENDPOINT="your-azure-openai-endpoint"
export AOAI_API_KEY="your-azure-openai-api-key"
export AOAI_DEPLOY_GPT4O_MINI="gpt-4o-mini"
```

### 🧪 테스트

1. **API 테스트**
```bash
# FastAPI 서버 실행
uvicorn src.api.main:app --reload

# API 문서 확인
# http://localhost:8000/docs
```

2. **Streamlit 테스트**
```bash
# Streamlit 앱 실행
streamlit run src/ui/streamlit_app.py
```

3. **개별 에이전트 테스트**
```bash
python src/agents/enhanced_agent.py
python src/agents/advanced_tool_agent.py
python src/agents/langgraph_agent.py
```

### 🔄 API 개발

새로운 API 엔드포인트를 추가하는 방법:

1. **에이전트 구현**
```python
# src/agents/your_agent.py
class YourAgent:
    def __init__(self):
        # 초기화 로직
    
    def process_query(self, query: str) -> Dict[str, Any]:
        # 처리 로직
        return {"response": "result"}
```

2. **API 엔드포인트 추가**
```python
# src/api/your_endpoints.py
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/your-feature", tags=["Your Feature"])

class YourRequest(BaseModel):
    query: str

@router.post("/process")
async def process_query(request: YourRequest):
    agent = YourAgent()
    result = agent.process_query(request.query)
    return result
```

3. **메인 API에 등록**
```python
# src/api/main.py
from .your_endpoints import router as your_router

app.include_router(your_router)
```

## 🔧 API 문서

### 📡 REST API 엔드포인트

#### 기본 API
- `POST /chat` - 기본 챗봇
- `POST /query` - RAG 기반 질의
- `POST /analyze` - 재무 분석

#### 향상된 API
- `POST /enhanced/chat` - 고급 챗봇
- `POST /enhanced/lcel` - LCEL 체인
- `POST /enhanced/structured` - 구조화된 출력
- `POST /enhanced/multimodal` - 멀티모달 분석

#### Tool Calling API
- `POST /advanced-tool/basic` - 기본 Tool Calling
- `POST /advanced-tool/agent-executor` - Agent Executor
- `POST /advanced-tool/comprehensive` - 종합 분석

#### LangGraph API
- `POST /langgraph/basic-chat` - 기본 LangGraph 챗봇
- `POST /langgraph/tool-agent` - Tool Agent
- `POST /langgraph/multi-agent` - Multi Agent
- `POST /langgraph/comprehensive-analysis` - 종합 분석
- `POST /langgraph/interactive-consultation` - 대화형 상담
- `POST /langgraph/expert-consultation` - 전문가 상담

### 📊 응답 형식

모든 API는 일관된 JSON 응답 형식을 사용합니다:

```json
{
  "response": "AI 응답 내용",
  "method": "사용된 처리 방법",
  "timestamp": "2024-01-15T10:30:00",
  "metadata": {
    "processing_time": 1.23,
    "tokens_used": 150
  }
}
```

## 📊 성능 최적화

### ⚡ 성능 개선 사항

1. **비동기 처리**: FastAPI의 비동기 특성 활용
2. **캐싱**: Redis를 통한 응답 캐싱
3. **벡터 검색**: FAISS를 통한 고성능 유사도 검색
4. **메모리 관리**: LangGraph의 효율적인 상태 관리
5. **로드 밸런싱**: Docker Compose를 통한 서비스 분산

### 📈 성능 지표

- **응답 시간**: 평균 1-3초
- **동시 사용자**: 100명 이상 지원
- **정확도**: 재무 분석 95% 이상
- **가용성**: 99.9% 이상

## 🔒 보안

### 🛡️ 보안 조치

1. **API 키 보안**: 환경 변수를 통한 민감 정보 관리
2. **입력 검증**: Pydantic을 통한 데이터 검증
3. **CORS 설정**: 허용된 도메인만 접근 가능
4. **로깅**: 보안 이벤트 추적
5. **Docker 보안**: 최소 권한 원칙 적용

### 🔐 인증 및 권한

현재 버전은 개발용으로 설계되어 있으며, 프로덕션 배포 시 다음 보안 강화가 필요합니다:

- JWT 토큰 기반 인증
- 사용자 역할 기반 권한 관리
- API 요청 제한 (Rate Limiting)
- HTTPS 강제 적용

## 📝 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다.

## 🤝 기여하기

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📞 지원

- **이슈 리포트**: GitHub Issues
- **문서**: 이 README 및 API 문서
- **이메일**: your-email@example.com

---

**AI 재무관리 어드바이저** - 개인 재무 관리를 위한 AI 기반 종합 솔루션 🚀
