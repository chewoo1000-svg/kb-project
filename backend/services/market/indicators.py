"""C. 시장 지표 계산 함수 — 순수 함수만, 데이터 로드 없음."""
import pandas as pd


def daily_returns(s: pd.Series) -> pd.Series:
    return (s.pct_change() * 100).round(2)


def excess_return(port_pct: pd.Series, index_pct: pd.Series) -> pd.Series:
    return (port_pct - index_pct).round(2)


def drawdown(s: pd.Series) -> pd.Series:
    peak = s.cummax()
    return ((s - peak) / peak * 100).round(2)


def relative_strength(port: pd.Series, index: pd.Series) -> pd.Series:
    return ((port / port.iloc[0]) / (index / index.iloc[0])).round(4)
