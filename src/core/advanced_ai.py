"""
고급 AI 기능 모듈
감정 분석, 시장 예측, 리스크 평가 등 고급 AI 기능
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
import logging
import re
from textblob import TextBlob
import yfinance as yf

logger = logging.getLogger(__name__)

class AdvancedAIFeatures:
    """고급 AI 기능 클래스"""
    
    def __init__(self):
        self.sentiment_cache = {}
        self.prediction_cache = {}
        
    def analyze_market_sentiment(self, text_data: List[str]) -> Dict[str, Any]:
        """시장 감정 분석"""
        try:
            sentiments = []
            for text in text_data:
                # TextBlob을 사용한 감정 분석
                blob = TextBlob(text)
                sentiment_score = blob.sentiment.polarity
                subjectivity_score = blob.sentiment.subjectivity
                
                sentiments.append({
                    "text": text[:100] + "..." if len(text) > 100 else text,
                    "sentiment": sentiment_score,
                    "subjectivity": subjectivity_score,
                    "sentiment_label": self._get_sentiment_label(sentiment_score)
                })
            
            # 전체 감정 점수 계산
            avg_sentiment = np.mean([s["sentiment"] for s in sentiments])
            avg_subjectivity = np.mean([s["subjectivity"] for s in sentiments])
            
            # 감정 분포 계산
            positive_count = sum(1 for s in sentiments if s["sentiment"] > 0.1)
            negative_count = sum(1 for s in sentiments if s["sentiment"] < -0.1)
            neutral_count = len(sentiments) - positive_count - negative_count
            
            return {
                "overall_sentiment": avg_sentiment,
                "overall_subjectivity": avg_subjectivity,
                "sentiment_distribution": {
                    "positive": positive_count,
                    "negative": negative_count,
                    "neutral": neutral_count,
                    "total": len(sentiments)
                },
                "sentiment_label": self._get_sentiment_label(avg_sentiment),
                "market_mood": self._get_market_mood(avg_sentiment),
                "detailed_sentiments": sentiments
            }
            
        except Exception as e:
            logger.error(f"감정 분석 실패: {e}")
            return {"error": f"감정 분석 실패: {str(e)}"}
    
    def _get_sentiment_label(self, score: float) -> str:
        """감정 점수를 라벨로 변환"""
        if score > 0.3:
            return "매우 긍정적"
        elif score > 0.1:
            return "긍정적"
        elif score < -0.3:
            return "매우 부정적"
        elif score < -0.1:
            return "부정적"
        else:
            return "중립적"
    
    def _get_market_mood(self, sentiment: float) -> str:
        """시장 분위기 판단"""
        if sentiment > 0.2:
            return "낙관적"
        elif sentiment > 0:
            return "약간 낙관적"
        elif sentiment < -0.2:
            return "비관적"
        elif sentiment < 0:
            return "약간 비관적"
        else:
            return "중립적"
    
    def predict_market_trend(self, 
                           symbol: str, 
                           days: int = 30,
                           confidence_level: float = 0.8) -> Dict[str, Any]:
        """시장 트렌드 예측"""
        try:
            # 주가 데이터 수집
            ticker = yf.Ticker(symbol)
            data = ticker.history(period="1y")
            
            if data.empty:
                return {"error": "데이터를 수집할 수 없습니다."}
            
            # 기술적 지표 계산
            data['SMA_20'] = data['Close'].rolling(window=20).mean()
            data['SMA_50'] = data['Close'].rolling(window=50).mean()
            data['RSI'] = self._calculate_rsi(data['Close'])
            data['MACD'] = self._calculate_macd(data['Close'])
            
            # 최근 데이터 분석
            recent_data = data.tail(30)
            current_price = recent_data['Close'].iloc[-1]
            
            # 트렌드 분석
            price_trend = self._analyze_price_trend(recent_data)
            volume_trend = self._analyze_volume_trend(recent_data)
            technical_signals = self._analyze_technical_signals(recent_data)
            
            # 예측 신뢰도 계산
            confidence = self._calculate_prediction_confidence(
                price_trend, volume_trend, technical_signals
            )
            
            # 예측 결과 (numpy 타입을 Python 기본 타입으로 변환)
            prediction = {
                "symbol": symbol,
                "current_price": float(current_price),
                "prediction_days": int(days),
                "trend_direction": price_trend["direction"],
                "trend_strength": float(price_trend["strength"]),
                "expected_change_percent": float(price_trend["expected_change"]),
                "confidence_level": float(confidence),
                "technical_signals": technical_signals,
                "volume_analysis": volume_trend,
                "risk_level": self._assess_risk_level(confidence, float(price_trend["volatility"])),
                "recommendation": self._generate_recommendation(
                    price_trend, confidence, technical_signals
                )
            }
            
            # numpy 타입을 완전히 제거하기 위해 딕셔너리를 새로 생성
            clean_prediction = {}
            for key, value in prediction.items():
                if isinstance(value, dict):
                    clean_prediction[key] = {}
                    for sub_key, sub_value in value.items():
                        if hasattr(sub_value, 'item'):  # numpy 타입인 경우
                            clean_prediction[key][sub_key] = sub_value.item()
                        else:
                            clean_prediction[key][sub_key] = sub_value
                elif hasattr(value, 'item'):  # numpy 타입인 경우
                    clean_prediction[key] = value.item()
                else:
                    clean_prediction[key] = value
            
            return clean_prediction
            
        except Exception as e:
            logger.error(f"시장 예측 실패: {e}")
            return {"error": f"예측 실패: {str(e)}"}
    
    def _calculate_rsi(self, prices: pd.Series, period: int = 14) -> pd.Series:
        """RSI 계산"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def _calculate_macd(self, prices: pd.Series, 
                       fast: int = 12, slow: int = 26, signal: int = 9) -> pd.Series:
        """MACD 계산"""
        ema_fast = prices.ewm(span=fast).mean()
        ema_slow = prices.ewm(span=slow).mean()
        macd = ema_fast - ema_slow
        signal_line = macd.ewm(span=signal).mean()
        return macd - signal_line
    
    def _analyze_price_trend(self, data: pd.DataFrame) -> Dict[str, Any]:
        """가격 트렌드 분석"""
        try:
            prices = data['Close']
            
            # 선형 회귀를 통한 트렌드 분석
            x = np.arange(len(prices))
            slope, intercept = np.polyfit(x, prices, 1)
            
            # 트렌드 방향
            if slope > 0:
                direction = "상승"
            elif slope < 0:
                direction = "하락"
            else:
                direction = "횡보"
            
            # 트렌드 강도 (R² 값)
            y_pred = slope * x + intercept
            r_squared = 1 - np.sum((prices - y_pred) ** 2) / np.sum((prices - prices.mean()) ** 2)
            
            # 변동성
            volatility = prices.pct_change().std()
            
            # 예상 변화율 (30일 기준)
            expected_change = slope * 30 / prices.iloc[-1] * 100
            
            return {
                "direction": direction,
                "strength": r_squared,
                "slope": slope,
                "volatility": volatility,
                "expected_change": expected_change
            }
            
        except Exception as e:
            logger.error(f"가격 트렌드 분석 실패: {e}")
            return {"direction": "불명확", "strength": 0, "expected_change": 0}
    
    def _analyze_volume_trend(self, data: pd.DataFrame) -> Dict[str, Any]:
        """거래량 트렌드 분석"""
        try:
            volume = data['Volume']
            prices = data['Close']
            
            # 거래량 이동평균
            volume_sma = volume.rolling(window=20).mean()
            current_volume = volume.iloc[-1]
            avg_volume = volume_sma.iloc[-1]
            
            # 가격 변화와 거래량 상관관계
            price_change = prices.pct_change()
            volume_change = volume.pct_change()
            correlation = price_change.corr(volume_change)
            
            return {
                "current_volume": float(current_volume),
                "average_volume": float(avg_volume),
                "volume_ratio": float(current_volume / avg_volume if avg_volume > 0 else 1),
                "volume_trend": "높음" if current_volume > avg_volume * 1.5 else "보통" if current_volume > avg_volume else "낮음",
                "price_volume_correlation": float(correlation) if not pd.isna(correlation) else 0.0
            }
            
        except Exception as e:
            logger.error(f"거래량 분석 실패: {e}")
            return {"volume_trend": "불명확"}
    
    def _analyze_technical_signals(self, data: pd.DataFrame) -> Dict[str, Any]:
        """기술적 지표 신호 분석"""
        try:
            signals = {}
            
            # RSI 신호
            rsi = data['RSI'].iloc[-1]
            if rsi > 70:
                signals['rsi'] = "과매수"
            elif rsi < 30:
                signals['rsi'] = "과매도"
            else:
                signals['rsi'] = "중립"
            
            # MACD 신호
            macd = data['MACD'].iloc[-1]
            if macd > 0:
                signals['macd'] = "매수 신호"
            else:
                signals['macd'] = "매도 신호"
            
            # 이동평균 신호
            sma_20 = data['SMA_20'].iloc[-1]
            sma_50 = data['SMA_50'].iloc[-1]
            current_price = data['Close'].iloc[-1]
            
            if current_price > sma_20 > sma_50:
                signals['moving_averages'] = "강한 상승"
            elif current_price > sma_20 and sma_20 < sma_50:
                signals['moving_averages'] = "약한 상승"
            elif current_price < sma_20 < sma_50:
                signals['moving_averages'] = "강한 하락"
            else:
                signals['moving_averages'] = "약한 하락"
            
            # 종합 신호
            bullish_signals = sum(1 for signal in signals.values() 
                                if "매수" in signal or "상승" in signal)
            bearish_signals = sum(1 for signal in signals.values() 
                                if "매도" in signal or "하락" in signal)
            
            if bullish_signals > bearish_signals:
                signals['overall'] = "매수 우세"
            elif bearish_signals > bullish_signals:
                signals['overall'] = "매도 우세"
            else:
                signals['overall'] = "중립"
            
            return signals
            
        except Exception as e:
            logger.error(f"기술적 신호 분석 실패: {e}")
            return {"overall": "불명확"}
    
    def _calculate_prediction_confidence(self, 
                                       price_trend: Dict[str, Any],
                                       volume_trend: Dict[str, Any],
                                       technical_signals: Dict[str, Any]) -> float:
        """예측 신뢰도 계산"""
        try:
            confidence = 0.5  # 기본 신뢰도
            
            # 트렌드 강도에 따른 조정
            trend_strength = price_trend.get("strength", 0)
            confidence += trend_strength * 0.2
            
            # 거래량 신뢰도
            volume_ratio = volume_trend.get("volume_ratio", 1)
            if 0.8 <= volume_ratio <= 1.2:
                confidence += 0.1  # 정상 거래량
            elif volume_ratio > 1.5:
                confidence += 0.15  # 높은 거래량 (신뢰도 증가)
            
            # 기술적 신호 일치도
            overall_signal = technical_signals.get("overall", "")
            if "우세" in overall_signal:
                confidence += 0.1
            
            # 변동성에 따른 조정
            volatility = price_trend.get("volatility", 0)
            if volatility < 0.02:  # 낮은 변동성
                confidence += 0.05
            elif volatility > 0.05:  # 높은 변동성
                confidence -= 0.1
            
            return min(max(confidence, 0.1), 0.95)  # 0.1 ~ 0.95 범위로 제한
            
        except Exception as e:
            logger.error(f"신뢰도 계산 실패: {e}")
            return 0.5
    
    def _assess_risk_level(self, confidence: float, volatility: float) -> str:
        """리스크 수준 평가"""
        if confidence < 0.3 or volatility > 0.05:
            return "높음"
        elif confidence < 0.6 or volatility > 0.03:
            return "중간"
        else:
            return "낮음"
    
    def _generate_recommendation(self, 
                               price_trend: Dict[str, Any],
                               confidence: float,
                               technical_signals: Dict[str, Any]) -> str:
        """투자 권장사항 생성"""
        try:
            direction = price_trend.get("direction", "불명확")
            strength = price_trend.get("strength", 0)
            overall_signal = technical_signals.get("overall", "")
            
            if confidence < 0.4:
                return "신뢰도가 낮아 권장사항을 제시하기 어렵습니다."
            
            if direction == "상승" and strength > 0.3:
                if "매수" in overall_signal:
                    return "강한 매수 신호: 상승 트렌드가 명확하고 기술적 지표도 긍정적입니다."
                else:
                    return "매수 고려: 상승 트렌드가 있으나 기술적 지표를 주의깊게 관찰하세요."
            
            elif direction == "하락" and strength > 0.3:
                if "매도" in overall_signal:
                    return "매도 권장: 하락 트렌드가 명확하고 기술적 지표도 부정적입니다."
                else:
                    return "매도 고려: 하락 트렌드가 있으나 기술적 지표를 주의깊게 관찰하세요."
            
            else:
                return "관망 권장: 명확한 트렌드가 없어 관망하는 것이 좋겠습니다."
                
        except Exception as e:
            logger.error(f"권장사항 생성 실패: {e}")
            return "분석 중 오류가 발생했습니다."

# 전역 인스턴스
advanced_ai = AdvancedAIFeatures()
