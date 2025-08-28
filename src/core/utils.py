"""
유틸리티 함수 모듈
공통으로 사용되는 유틸리티 함수들을 제공합니다.
"""

import logging
import json
import re
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from pathlib import Path
import pandas as pd
import yfinance as yf

from .config import settings

# 로깅 설정
def setup_logging():
    """로깅 설정을 초기화합니다."""
    logging.basicConfig(
        level=getattr(logging, settings.log_level),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(settings.log_file),
            logging.StreamHandler()
        ]
    )

# 금융 데이터 유틸리티
def get_stock_data(symbol: str, period: str = "1y") -> pd.DataFrame:
    """주식 데이터를 가져옵니다."""
    try:
        ticker = yf.Ticker(symbol)
        data = ticker.history(period=period)
        return data
    except Exception as e:
        logging.error(f"주식 데이터 가져오기 실패: {symbol}, 오류: {e}")
        return pd.DataFrame()

def calculate_returns(prices: pd.Series) -> Dict[str, float]:
    """수익률을 계산합니다."""
    if len(prices) < 2:
        return {"total_return": 0.0, "annualized_return": 0.0}
    
    total_return = (prices.iloc[-1] - prices.iloc[0]) / prices.iloc[0]
    days = (prices.index[-1] - prices.index[0]).days
    annualized_return = ((prices.iloc[-1] / prices.iloc[0]) ** (365 / days)) - 1
    
    return {
        "total_return": total_return * 100,
        "annualized_return": annualized_return * 100
    }

def format_currency(amount: float) -> str:
    """금액을 통화 형식으로 포맷합니다."""
    return f"₩{amount:,.0f}"

def format_percentage(value: float) -> str:
    """백분율을 포맷합니다."""
    return f"{value:.2f}%"

# 텍스트 처리 유틸리티
def clean_text(text: str) -> str:
    """텍스트를 정리합니다."""
    # 불필요한 공백 제거
    text = re.sub(r'\s+', ' ', text.strip())
    # 특수 문자 정리
    text = re.sub(r'[^\w\s\-.,!?()]', '', text)
    return text

def extract_numbers(text: str) -> List[float]:
    """텍스트에서 숫자를 추출합니다."""
    numbers = re.findall(r'\d+\.?\d*', text)
    return [float(num) for num in numbers]

def extract_currency(text: str) -> Optional[float]:
    """텍스트에서 통화 금액을 추출합니다."""
    # ₩, $, € 등의 통화 기호와 숫자 패턴 찾기
    patterns = [
        r'₩\s*([\d,]+\.?\d*)',
        r'\$\s*([\d,]+\.?\d*)',
        r'€\s*([\d,]+\.?\d*)',
        r'([\d,]+\.?\d*)\s*원',
        r'([\d,]+\.?\d*)\s*달러',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            amount_str = match.group(1).replace(',', '')
            return float(amount_str)
    
    return None

# 날짜 유틸리티
def parse_date(date_str: str) -> Optional[datetime]:
    """날짜 문자열을 파싱합니다."""
    formats = [
        '%Y-%m-%d',
        '%Y/%m/%d',
        '%d/%m/%Y',
        '%m/%d/%Y',
        '%Y년 %m월 %d일',
    ]
    
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    
    return None

def get_age_from_birthdate(birthdate: datetime) -> int:
    """생년월일로부터 나이를 계산합니다."""
    today = datetime.now()
    age = today.year - birthdate.year
    if today.month < birthdate.month or (today.month == birthdate.month and today.day < birthdate.day):
        age -= 1
    return age

# 파일 유틸리티
def save_json(data: Dict[str, Any], filepath: str):
    """데이터를 JSON 파일로 저장합니다."""
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_json(filepath: str) -> Dict[str, Any]:
    """JSON 파일을 로드합니다."""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def ensure_file_exists(filepath: str, default_content: str = ""):
    """파일이 존재하지 않으면 생성합니다."""
    path = Path(filepath)
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(default_content)

# 검증 유틸리티
def validate_email(email: str) -> bool:
    """이메일 형식을 검증합니다."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_phone(phone: str) -> bool:
    """전화번호 형식을 검증합니다."""
    # 한국 전화번호 형식 (010-1234-5678, 02-123-4567 등)
    pattern = r'^(\d{2,3})-?(\d{3,4})-?(\d{4})$'
    return re.match(pattern, phone) is not None

def validate_ssn(ssn: str) -> bool:
    """주민등록번호 형식을 검증합니다."""
    # 주민등록번호 형식 (123456-1234567)
    pattern = r'^\d{6}-\d{7}$'
    if not re.match(pattern, ssn):
        return False
    
    # 체크섬 검증
    ssn = ssn.replace('-', '')
    weights = [2, 3, 4, 5, 6, 7, 8, 9, 2, 3, 4, 5]
    
    checksum = sum(int(ssn[i]) * weights[i] for i in range(12))
    remainder = checksum % 11
    check_digit = (11 - remainder) % 10
    
    return int(ssn[12]) == check_digit

# 보안 유틸리티
def mask_sensitive_data(text: str, data_type: str = "ssn") -> str:
    """민감한 데이터를 마스킹합니다."""
    if data_type == "ssn":
        # 주민등록번호 마스킹 (123456-*******)
        return re.sub(r'(\d{6})-\d{7}', r'\1-*******', text)
    elif data_type == "phone":
        # 전화번호 마스킹 (010-****-5678)
        return re.sub(r'(\d{3})-\d{4}-(\d{4})', r'\1-****-\2', text)
    elif data_type == "email":
        # 이메일 마스킹 (a***@example.com)
        return re.sub(r'(\w{1})\w+(@\w+\.\w+)', r'\1***\2', text)
    
    return text

# 성능 유틸리티
def measure_time(func):
    """함수 실행 시간을 측정하는 데코레이터"""
    import time
    
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        logging.info(f"{func.__name__} 실행 시간: {end_time - start_time:.2f}초")
        return result
    
    return wrapper

# 초기화
setup_logging()
