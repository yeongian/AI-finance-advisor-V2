"""
포트폴리오 시뮬레이션 및 백테스팅 모듈
투자 전략의 성과를 시뮬레이션하고 분석
"""

import pandas as pd
import numpy as np
import yfinance as yf
import plotly.graph_objects as go
import plotly.express as px
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class PortfolioSimulator:
    """포트폴리오 시뮬레이터"""
    
    def __init__(self):
        self.risk_free_rate = 0.02  # 무위험 수익률 (2%)
        
    def calculate_portfolio_metrics(self, returns: pd.Series) -> Dict[str, float]:
        """포트폴리오 성과 지표 계산"""
        try:
            # 기본 지표
            total_return = (1 + returns).prod() - 1
            annual_return = (1 + total_return) ** (252 / len(returns)) - 1
            volatility = returns.std() * np.sqrt(252)
            
            # 샤프 비율
            excess_returns = returns - self.risk_free_rate / 252
            sharpe_ratio = excess_returns.mean() / returns.std() * np.sqrt(252)
            
            # 최대 낙폭
            cumulative_returns = (1 + returns).cumprod()
            running_max = cumulative_returns.expanding().max()
            drawdown = (cumulative_returns - running_max) / running_max
            max_drawdown = drawdown.min()
            
            # VaR (Value at Risk) - 95% 신뢰수준
            var_95 = np.percentile(returns, 5)
            
            return {
                "total_return": total_return,
                "annual_return": annual_return,
                "volatility": volatility,
                "sharpe_ratio": sharpe_ratio,
                "max_drawdown": max_drawdown,
                "var_95": var_95,
                "calmar_ratio": annual_return / abs(max_drawdown) if max_drawdown != 0 else 0
            }
        except Exception as e:
            logger.error(f"포트폴리오 지표 계산 실패: {e}")
            return {}
    
    def simulate_portfolio(self, 
                          symbols: List[str], 
                          weights: List[float],
                          start_date: str,
                          end_date: str = None,
                          initial_investment: float = 10000000) -> Dict[str, Any]:
        """포트폴리오 시뮬레이션"""
        try:
            if end_date is None:
                end_date = datetime.now().strftime('%Y-%m-%d')
            
            # 주가 데이터 수집
            portfolio_data = {}
            for symbol in symbols:
                try:
                    ticker = yf.Ticker(symbol)
                    data = ticker.history(start=start_date, end=end_date)
                    if not data.empty:
                        portfolio_data[symbol] = data['Close']
                except Exception as e:
                    logger.error(f"데이터 수집 실패 {symbol}: {e}")
            
            if not portfolio_data:
                return {"error": "데이터를 수집할 수 없습니다."}
            
            # 데이터프레임 생성
            df = pd.DataFrame(portfolio_data)
            df = df.dropna()
            
            # 수익률 계산
            returns = df.pct_change().dropna()
            
            # 포트폴리오 수익률 계산
            portfolio_returns = (returns * weights).sum(axis=1)
            
            # 성과 지표 계산
            metrics = self.calculate_portfolio_metrics(portfolio_returns)
            
            # 누적 수익률 계산
            cumulative_returns = (1 + portfolio_returns).cumprod()
            portfolio_value = initial_investment * cumulative_returns
            
            # 결과 반환
            return {
                "symbols": symbols,
                "weights": weights,
                "start_date": start_date,
                "end_date": end_date,
                "initial_investment": initial_investment,
                "final_value": portfolio_value.iloc[-1],
                "total_return": metrics.get("total_return", 0),
                "annual_return": metrics.get("annual_return", 0),
                "volatility": metrics.get("volatility", 0),
                "sharpe_ratio": metrics.get("sharpe_ratio", 0),
                "max_drawdown": metrics.get("max_drawdown", 0),
                "portfolio_returns": portfolio_returns,
                "portfolio_value": portfolio_value,
                "cumulative_returns": cumulative_returns
            }
            
        except Exception as e:
            logger.error(f"포트폴리오 시뮬레이션 실패: {e}")
            return {"error": f"시뮬레이션 실패: {str(e)}"}
    
    def compare_portfolios(self, 
                          portfolios: List[Dict[str, Any]]) -> Dict[str, Any]:
        """여러 포트폴리오 비교"""
        try:
            comparison = {
                "portfolios": [],
                "summary": {}
            }
            
            for i, portfolio in enumerate(portfolios):
                if "error" not in portfolio:
                    comparison["portfolios"].append({
                        "name": f"포트폴리오 {i+1}",
                        "total_return": portfolio.get("total_return", 0),
                        "annual_return": portfolio.get("annual_return", 0),
                        "volatility": portfolio.get("volatility", 0),
                        "sharpe_ratio": portfolio.get("sharpe_ratio", 0),
                        "max_drawdown": portfolio.get("max_drawdown", 0)
                    })
            
            # 요약 통계
            if comparison["portfolios"]:
                returns = [p["total_return"] for p in comparison["portfolios"]]
                sharpe_ratios = [p["sharpe_ratio"] for p in comparison["portfolios"]]
                
                comparison["summary"] = {
                    "best_return": max(returns),
                    "worst_return": min(returns),
                    "avg_return": np.mean(returns),
                    "best_sharpe": max(sharpe_ratios),
                    "worst_sharpe": min(sharpe_ratios),
                    "avg_sharpe": np.mean(sharpe_ratios)
                }
            
            return comparison
            
        except Exception as e:
            logger.error(f"포트폴리오 비교 실패: {e}")
            return {"error": f"비교 실패: {str(e)}"}
    
    def create_efficient_frontier(self, 
                                 symbols: List[str],
                                 start_date: str,
                                 end_date: str = None,
                                 num_portfolios: int = 1000) -> Dict[str, Any]:
        """효율적 프론티어 생성"""
        try:
            if end_date is None:
                end_date = datetime.now().strftime('%Y-%m-%d')
            
            # 주가 데이터 수집
            portfolio_data = {}
            for symbol in symbols:
                try:
                    ticker = yf.Ticker(symbol)
                    data = ticker.history(start=start_date, end=end_date)
                    if not data.empty:
                        portfolio_data[symbol] = data['Close']
                except Exception as e:
                    logger.error(f"데이터 수집 실패 {symbol}: {e}")
            
            if not portfolio_data:
                return {"error": "데이터를 수집할 수 없습니다."}
            
            # 수익률 계산
            df = pd.DataFrame(portfolio_data)
            returns = df.pct_change().dropna()
            
            # 랜덤 포트폴리오 생성
            portfolios = []
            for _ in range(num_portfolios):
                weights = np.random.random(len(symbols))
                weights = weights / weights.sum()
                
                portfolio_return = (returns * weights).sum(axis=1)
                metrics = self.calculate_portfolio_metrics(portfolio_return)
                
                portfolios.append({
                    "weights": weights.tolist(),
                    "return": metrics.get("annual_return", 0),
                    "volatility": metrics.get("volatility", 0),
                    "sharpe_ratio": metrics.get("sharpe_ratio", 0)
                })
            
            return {
                "symbols": symbols,
                "portfolios": portfolios,
                "efficient_frontier": self._find_efficient_frontier(portfolios)
            }
            
        except Exception as e:
            logger.error(f"효율적 프론티어 생성 실패: {e}")
            return {"error": f"생성 실패: {str(e)}"}
    
    def _find_efficient_frontier(self, portfolios: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """효율적 프론티어 포트폴리오 찾기"""
        try:
            # 수익률별로 정렬
            sorted_portfolios = sorted(portfolios, key=lambda x: x["return"])
            
            efficient_frontier = []
            max_sharpe = -np.inf
            
            for portfolio in sorted_portfolios:
                if portfolio["sharpe_ratio"] > max_sharpe:
                    efficient_frontier.append(portfolio)
                    max_sharpe = portfolio["sharpe_ratio"]
            
            return efficient_frontier
            
        except Exception as e:
            logger.error(f"효율적 프론티어 찾기 실패: {e}")
            return []

# 전역 인스턴스
portfolio_simulator = PortfolioSimulator()
