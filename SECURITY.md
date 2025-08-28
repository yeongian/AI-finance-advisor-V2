# 보안 가이드라인

## API 키 관리

### 1. 환경변수를 통한 API 키 관리

이 프로젝트는 **환경변수**를 통해 모든 민감한 정보를 관리합니다. 이는 보안 모범 사례를 따르는 방식입니다.

#### 지원하는 API 키들:
- **Azure OpenAI API 키**: `AOAI_API_KEY`
- **OpenAI API 키**: `OPENAI_API_KEY` (백업용)
- **Alpha Vantage API 키**: `ALPHA_VANTAGE_API_KEY` (선택사항)
- **Yahoo Finance API 키**: `YAHOO_FINANCE_API_KEY` (선택사항)

### 2. 환경변수 설정 방법

#### 개발 환경
```bash
# 1. 환경변수 파일 복사
cp env_example.txt .env

# 2. .env 파일 편집하여 실제 API 키 입력
# AOAI_API_KEY=your_actual_azure_openai_api_key
# OPENAI_API_KEY=your_actual_openai_api_key
```

#### 프로덕션 환경
```bash
# 시스템 환경변수 설정
export AOAI_API_KEY="your_actual_azure_openai_api_key"
export AOAI_ENDPOINT="https://your-endpoint.openai.azure.com/"
```

### 3. 보안 조치

#### .gitignore를 통한 파일 보호
```gitignore
# 환경변수 파일 (API 키 포함)
.env
.env.local
.env.production
```

#### 코드에서의 API 키 처리
```python
# src/core/config.py
class Settings(BaseSettings):
    # 환경변수에서 API 키 로드
    aoai_api_key: Optional[str] = os.getenv("AOAI_API_KEY")
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    
    class Config:
        env_file = ".env"  # .env 파일에서 로드
        case_sensitive = False
```

### 4. 보안 모범 사례 준수

#### ✅ 구현된 보안 조치:
1. **환경변수 사용**: API 키를 코드에 하드코딩하지 않음
2. **Git 무시**: `.env` 파일이 Git에 커밋되지 않도록 `.gitignore` 설정
3. **타입 안전성**: Pydantic을 통한 설정 검증
4. **기본값 제공**: API 키가 없어도 로컬 모델로 대체 가능
5. **선택적 API**: 필수가 아닌 API는 선택적으로 사용

#### ✅ 추가 권장사항:
1. **API 키 순환**: 정기적으로 API 키 교체
2. **접근 제한**: API 키에 최소 권한만 부여
3. **모니터링**: API 사용량 및 비정상 접근 모니터링
4. **암호화**: 프로덕션에서는 환경변수 암호화 고려

### 5. 개발 환경 vs 프로덕션 환경

#### 개발 환경
- `.env` 파일 사용
- 디버그 모드 활성화
- 로컬 데이터베이스 사용

#### 프로덕션 환경
- 시스템 환경변수 사용
- 디버그 모드 비활성화
- 보안 강화된 데이터베이스 사용
- HTTPS 강제 사용

### 6. API 키 보안 체크리스트

- [ ] API 키가 코드에 하드코딩되지 않음
- [ ] `.env` 파일이 `.gitignore`에 포함됨
- [ ] 환경변수를 통한 API 키 관리
- [ ] API 키에 최소 권한만 부여
- [ ] 정기적인 API 키 순환 계획
- [ ] API 사용량 모니터링
- [ ] 프로덕션 환경에서 HTTPS 사용

### 7. 문제 해결

#### API 키 관련 오류
```bash
# 환경변수 확인
echo $AOAI_API_KEY

# .env 파일 확인 (개발 환경)
cat .env | grep API_KEY
```

#### 보안 감사
```bash
# Git 히스토리에서 API 키 검색
git log -p | grep -i "api_key\|password\|secret"

# 현재 코드에서 하드코딩된 키 검색
grep -r "sk-" src/
grep -r "your_api_key" src/
```

이 프로젝트는 **실제 서비스 개발 시 고려해야 할 보안 모범 사례**를 모두 준수하고 있습니다.
