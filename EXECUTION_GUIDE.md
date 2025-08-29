# 🚀 AI 재무관리 어드바이저 실행 가이드

> 상세한 설치 및 실행 방법 안내서

## 📋 목차

- [🔧 사전 요구사항](#-사전-요구사항)
- [⚙️ 환경 설정](#️-환경-설정)
- [🚀 실행 방법](#-실행-방법)
- [🔍 문제 해결](#-문제-해결)
- [📊 모니터링](#-모니터링)
- [🔄 업데이트](#-업데이트)

## 🔧 사전 요구사항

### 필수 소프트웨어

- **Python 3.9+**
- **Docker 20.10+** (선택사항)
- **Git**

### Azure OpenAI 설정

1. **Azure Portal에서 OpenAI 리소스 생성**
   - Azure Portal → OpenAI 서비스 → 리소스 생성
   - 지역: East Asia 또는 가까운 지역 선택
   - 가격 책정 계층: Standard 선택

2. **모델 배포**
   - Azure OpenAI Studio 접속
   - 모델 배포에서 다음 모델들 배포:
     - `gpt-4o-mini` (GPT-4o Mini)
     - `text-embedding-3-small` (임베딩 모델)

3. **API 키 및 엔드포인트 확인**
   - 리소스 관리 → 키 및 엔드포인트
   - 키 1 또는 키 2 복사
   - 엔드포인트 URL 복사

## ⚙️ 환경 설정

### 1. 저장소 클론

```bash
git clone <repository-url>
cd AI-finance-advisor
```

### 2. 환경변수 설정

```bash
# 환경변수 파일 복사
cp env_example.txt .env

# .env 파일 편집
notepad .env  # Windows
# 또는
nano .env     # Linux/Mac
```

### 3. 환경변수 내용

```bash
# Azure OpenAI 설정
AOAI_ENDPOINT=https://your-resource.openai.azure.com/
AOAI_API_KEY=your_azure_openai_api_key_here
AOAI_DEPLOY_GPT4O_MINI=gpt-4o-mini
AOAI_DEPLOY_EMBED_3_SMALL=text-embedding-3-small

# 애플리케이션 설정
APP_ENV=development
LOG_LEVEL=INFO
API_HOST=0.0.0.0
API_PORT=8000
STREAMLIT_PORT=8501

# 데이터베이스 설정 (선택사항)
REDIS_URL=redis://localhost:6379
CHROMA_DB_PATH=./data/chroma_db
```

### 4. Python 가상환경 설정

```bash
# 가상환경 생성
python -m venv venv

# 가상환경 활성화
# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate

# 의존성 설치
pip install -r requirements.txt
```

## 🚀 실행 방법

### 방법 1: 배치 파일 사용 (Windows 권장)

#### 1단계: 초기 설정
```bash
# 모든 서비스 중지 (기존 실행 중인 서비스가 있는 경우)
00_stop_all.bat

# 초기 설정 실행
01_initial_setup.bat
```

#### 2단계: 애플리케이션 실행
```bash
# 메인 애플리케이션 실행
02_start_app.bat
```

#### 3단계: Docker 실행 (선택사항)
```bash
# Docker로 실행 (별도 터미널에서)
03_start_docker.bat
```

### 방법 2: 수동 실행

#### 1단계: API 서버 실행
```bash
# 가상환경 활성화
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# API 서버 실행
python -m uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload
```

#### 2단계: Streamlit 실행 (새 터미널)
```bash
# 가상환경 활성화
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# Streamlit 실행
python -m streamlit run main.py --server.port 8501
```

### 방법 3: Docker 실행

#### 1단계: Docker 이미지 빌드
```bash
docker build -t ai-finance-advisor .
```

#### 2단계: Docker Compose 실행
```bash
docker-compose up -d
```

#### 3단계: 로그 확인
```bash
docker-compose logs -f
```

## 🔍 문제 해결

### 일반적인 문제들

#### 1. API 서버 연결 실패

**증상**: "API 서버에 연결할 수 없습니다" 메시지

**해결 방법**:
```bash
# 1. API 서버 상태 확인
curl http://localhost:8000/health

# 2. 포트 사용 확인
netstat -an | findstr :8000  # Windows
lsof -i :8000               # Linux/Mac

# 3. API 서버 재시작
python -m uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload
```

#### 2. Azure OpenAI 연결 실패

**증상**: "Azure OpenAI 서비스 연결 오류"

**해결 방법**:
```bash
# 1. 환경변수 확인
echo $AOAI_ENDPOINT
echo $AOAI_API_KEY

# 2. .env 파일 확인
cat .env

# 3. Azure OpenAI Studio에서 모델 배포 확인
# https://oai.azure.com/
```

#### 3. 의존성 설치 오류

**증상**: `pip install` 실패

**해결 방법**:
```bash
# 1. Python 버전 확인
python --version

# 2. pip 업그레이드
python -m pip install --upgrade pip

# 3. 가상환경 재생성
rm -rf venv
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# 4. 의존성 재설치
pip install -r requirements.txt
```

#### 4. 메모리 부족 오류

**증상**: "Out of memory" 또는 성능 저하

**해결 방법**:
```bash
# 1. 불필요한 프로세스 종료
taskkill /f /im python.exe  # Windows
pkill python               # Linux/Mac

# 2. Docker 리소스 제한 확인
docker stats

# 3. 로그 파일 정리
rm -rf logs/*.log
```

### 로그 확인

#### API 서버 로그
```bash
# 실시간 로그 확인
tail -f logs/app.log

# 에러 로그만 확인
grep "ERROR" logs/app.log
```

#### Streamlit 로그
```bash
# Streamlit 로그 확인
tail -f logs/streamlit_app.log
```

#### Docker 로그
```bash
# 컨테이너 로그 확인
docker-compose logs -f

# 특정 서비스 로그
docker-compose logs -f api
docker-compose logs -f streamlit
```

## 📊 모니터링

### 성능 모니터링

#### 1. API 응답 시간 확인
```bash
# API 헬스체크
curl -w "@curl-format.txt" -o /dev/null -s http://localhost:8000/health
```

#### 2. 메모리 사용량 확인
```bash
# 프로세스별 메모리 사용량
ps aux | grep python

# Docker 컨테이너 리소스 사용량
docker stats
```

#### 3. 디스크 사용량 확인
```bash
# 데이터 디렉토리 크기
du -sh data/
du -sh logs/
```

### 로그 분석

#### 1. 에러 패턴 분석
```bash
# 에러 발생 빈도
grep "ERROR" logs/app.log | wc -l

# 최근 에러 확인
grep "ERROR" logs/app.log | tail -10
```

#### 2. 성능 지표 추출
```bash
# 평균 응답 시간
grep "API 응답" logs/app.log | awk '{print $NF}' | awk -F'초' '{sum+=$1; count++} END {print "평균: " sum/count "초"}'
```

## 🔄 업데이트

### 코드 업데이트

#### 1. 최신 코드 가져오기
```bash
# 변경사항 백업 (필요시)
git stash

# 최신 코드 가져오기
git pull origin main

# 의존성 업데이트 확인
pip install -r requirements.txt --upgrade
```

#### 2. 데이터베이스 마이그레이션
```bash
# 벡터 DB 재생성 (필요시)
rm -rf data/chroma_db
python -c "from src.rag.vector_store import VectorStore; VectorStore().initialize()"
```

#### 3. 서비스 재시작
```bash
# 모든 서비스 중지
00_stop_all.bat

# 서비스 재시작
02_start_app.bat
```

### 환경변수 업데이트

#### 1. 새로운 환경변수 추가
```bash
# .env 파일에 새로운 변수 추가
echo "NEW_VARIABLE=value" >> .env
```

#### 2. 서비스 재시작
```bash
# 환경변수 변경 후 서비스 재시작 필요
00_stop_all.bat
02_start_app.bat
```

## 📞 지원

### 문제 리포트

문제가 발생했을 때 다음 정보를 포함하여 리포트해주세요:

1. **환경 정보**
   - OS 버전
   - Python 버전
   - Docker 버전 (사용 시)

2. **에러 메시지**
   - 전체 에러 로그
   - 스크린샷 (UI 관련 문제)

3. **재현 단계**
   - 문제 발생까지의 단계별 과정
   - 사용한 입력 데이터

4. **기대 동작**
   - 정상적으로 동작했을 때의 결과

### 유용한 명령어

```bash
# 시스템 정보 확인
python --version
pip --version
docker --version

# 서비스 상태 확인
netstat -an | findstr :8000  # Windows
lsof -i :8000               # Linux/Mac

# 로그 실시간 확인
tail -f logs/app.log

# 환경변수 확인
env | grep AOAI
```

---

**AI 재무관리 어드바이저 실행 가이드** - 성공적인 배포를 위한 완벽한 가이드 🚀
