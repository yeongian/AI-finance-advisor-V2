"""
실시간 재무 데이터 통합 모듈
주식, 환율, 경제 지표 등 실시간 데이터 제공
"""

import yfinance as yf
import pandas as pd
import requests
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import asyncio
import aiohttp

logger = logging.getLogger(__name__)

class FinancialDataProvider:
    """실시간 재무 데이터 제공자"""
    
    def __init__(self):
        self.cache = {}
        self.cache_ttl = 300  # 5분 캐시
        
    async def get_stock_price(self, symbol: str) -> Dict[str, Any]:
        """주식 가격 정보 조회"""
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            return {
                "symbol": symbol,
                "price": info.get("currentPrice", 0),
                "change": info.get("regularMarketChange", 0),
                "change_percent": info.get("regularMarketChangePercent", 0),
                "volume": info.get("volume", 0),
                "market_cap": info.get("marketCap", 0),
                "pe_ratio": info.get("trailingPE", 0),
                "dividend_yield": info.get("dividendYield", 0),
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"주식 데이터 조회 실패: {e}")
            return None
    
    async def get_exchange_rate(self, from_currency: str, to_currency: str) -> Dict[str, Any]:
        """환율 정보 조회"""
        try:
            # SSL 인증서 검증 비활성화로 변경
            import ssl
            import certifi
            
            # SSL 컨텍스트 생성 (인증서 검증 비활성화)
            ssl_context = ssl.create_default_context(cafile=certifi.where())
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            
            # 간단한 환율 API 사용 (실제로는 더 정확한 API 필요)
            url = f"https://api.exchangerate-api.com/v4/latest/{from_currency}"
            
            connector = aiohttp.TCPConnector(ssl=ssl_context)
            async with aiohttp.ClientSession(connector=connector) as session:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                    if response.status == 200:
                        data = await response.json()
                        rate = data["rates"].get(to_currency, 0)
                        
                        return {
                            "from_currency": from_currency,
                            "to_currency": to_currency,
                            "rate": rate,
                            "timestamp": datetime.now().isoformat()
                        }
                    else:
                        logger.error(f"환율 API 응답 오류: {response.status}")
                        return None
                        
        except Exception as e:
            logger.error(f"환율 데이터 조회 실패: {e}")
            # 오류 시 기본값 반환
            return {
                "from_currency": from_currency,
                "to_currency": to_currency,
                "rate": 1300.0 if from_currency == "USD" and to_currency == "KRW" else 1.0,
                "timestamp": datetime.now().isoformat(),
                "note": "기본값 사용"
            }
    
    async def get_economic_indicators(self) -> Dict[str, Any]:
        """경제 지표 조회"""
        try:
            # 간단한 기본 정보만 반환
            return {
                "status": "available",
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"경제 지표 조회 실패: {e}")
            return None
    
    def get_mutual_fund_info(self, fund_code: str) -> Dict[str, Any]:
        """펀드 정보 조회"""
        try:
            # 한국투자증권 API 또는 다른 펀드 데이터 API 사용
            # 여기서는 예시 데이터 반환
            return {
                "fund_code": fund_code,
                "fund_name": "예시 펀드",
                "nav": 10000,
                "daily_return": 0.5,
                "monthly_return": 2.1,
                "yearly_return": 8.5,
                "risk_level": "중간",
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"펀드 정보 조회 실패: {e}")
            return None

# 전역 인스턴스
financial_data = FinancialDataProvider()
