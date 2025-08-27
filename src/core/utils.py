"""
공통 유틸리티 함수들
"""

import logging
import os
from datetime import datetime
from typing import Dict, List, Any, Optional
import json
import pandas as pd

def setup_logging(log_file: str = "./logs/finance_advisor.log", log_level: str = "INFO"):
    """로깅 설정"""
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    
    return logging.getLogger(__name__)

def format_currency(amount: float, currency: str = "KRW") -> str:
    """통화 포맷팅"""
    if currency == "KRW":
        return f"{amount:,.0f}원"
    elif currency == "USD":
        return f"${amount:,.2f}"
    else:
        return f"{amount:,.2f} {currency}"

def calculate_percentage_change(old_value: float, new_value: float) -> float:
    """백분율 변화 계산"""
    if old_value == 0:
        return 0
    return ((new_value - old_value) / old_value) * 100

def validate_user_input(data: Dict[str, Any]) -> Dict[str, Any]:
    """사용자 입력 데이터 검증"""
    validated_data = {}
    
    # 필수 필드 검증
    required_fields = ['age', 'income', 'expenses']
    for field in required_fields:
        if field not in data:
            raise ValueError(f"필수 필드가 누락되었습니다: {field}")
    
    # 데이터 타입 및 범위 검증
    if not isinstance(data['age'], int) or data['age'] < 18 or data['age'] > 100:
        raise ValueError("나이는 18-100 사이의 정수여야 합니다.")
    
    if not isinstance(data['income'], (int, float)) or data['income'] < 0:
        raise ValueError("소득은 0 이상의 숫자여야 합니다.")
    
    if not isinstance(data['expenses'], (int, float)) or data['expenses'] < 0:
        raise ValueError("지출은 0 이상의 숫자여야 합니다.")
    
    return data

def save_user_data(user_id: str, data: Dict[str, Any], file_path: str = "./data/user_data/"):
    """사용자 데이터 저장"""
    os.makedirs(file_path, exist_ok=True)
    
    filename = f"{user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    file_path = os.path.join(file_path, filename)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    return file_path

def load_user_data(user_id: str, file_path: str = "./data/user_data/") -> Optional[Dict[str, Any]]:
    """사용자 데이터 로드"""
    # 가장 최근 파일 찾기
    files = [f for f in os.listdir(file_path) if f.startswith(user_id)]
    if not files:
        return None
    
    latest_file = max(files, key=lambda x: os.path.getctime(os.path.join(file_path, x)))
    
    with open(os.path.join(file_path, latest_file), 'r', encoding='utf-8') as f:
        return json.load(f)

def create_sample_data() -> Dict[str, Any]:
    """샘플 사용자 데이터 생성"""
    return {
        "user_id": "sample_user",
        "age": 30,
        "income": 50000000,  # 5천만원
        "expenses": 30000000,  # 3천만원
        "savings": 100000000,  # 1억원
        "investment_risk_tolerance": "moderate",  # low, moderate, high
        "financial_goals": [
            {"goal": "집 구매", "target_amount": 500000000, "target_year": 5},
            {"goal": "은퇴 준비", "target_amount": 1000000000, "target_year": 30}
        ],
        "current_investments": {
            "stocks": 20000000,
            "bonds": 10000000,
            "real_estate": 0,
            "crypto": 0
        },
        "monthly_expenses": {
            "housing": 8000000,
            "food": 500000,
            "transportation": 300000,
            "entertainment": 200000,
            "utilities": 200000,
            "insurance": 300000,
            "other": 1000000
        }
    }

def calculate_basic_metrics(income: float, expenses: float, savings: float) -> Dict[str, Any]:
    """기본 재무 지표 계산"""
    net_income = income - expenses
    savings_rate = (net_income / income) * 100 if income > 0 else 0
    emergency_fund_months = (savings / expenses) if expenses > 0 else 0
    
    return {
        "net_income": net_income,
        "savings_rate": savings_rate,
        "emergency_fund_months": emergency_fund_months,
        "debt_to_income_ratio": 0,  # 부채 정보가 없으므로 0
        "financial_health_score": min(100, max(0, savings_rate * 2 + min(emergency_fund_months * 10, 40)))
    }

def get_financial_advice_category(user_query: str) -> str:
    """사용자 질의를 기반으로 재무 상담 카테고리 분류"""
    query_lower = user_query.lower()
    
    if any(word in query_lower for word in ['예산', '지출', '수입', '저축']):
        return "budget"
    elif any(word in query_lower for word in ['투자', '주식', '펀드', '포트폴리오']):
        return "investment"
    elif any(word in query_lower for word in ['세금', '공제', '연말정산']):
        return "tax"
    elif any(word in query_lower for word in ['부동산', '집', '아파트']):
        return "real_estate"
    elif any(word in query_lower for word in ['은퇴', '연금', '노후']):
        return "retirement"
    else:
        return "general"

def format_financial_advice(advice: str, category: str) -> str:
    """재무 조언 포맷팅"""
    category_emojis = {
        "budget": "💰",
        "investment": "📈",
        "tax": "📋",
        "real_estate": "🏠",
        "retirement": "🎯",
        "general": "💡"
    }
    
    emoji = category_emojis.get(category, "💡")
    return f"{emoji} **{category.upper()} 조언**\n\n{advice}"
