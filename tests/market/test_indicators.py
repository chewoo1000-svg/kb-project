import pandas as pd
from backend.services.market.indicators import daily_returns, excess_return, drawdown, relative_strength


def test_daily_returns():
    assert list(daily_returns(pd.Series([100, 110, 99]))[1:]) == [10.0, -10.0]


def test_excess_and_drawdown():
    assert list(excess_return(pd.Series([1.0, 2.0]), pd.Series([0.5, 3.0]))) == [0.5, -1.0]
    assert list(drawdown(pd.Series([100, 120, 90]))) == [0.0, 0.0, -25.0]


def test_relative_strength_starts_at_one():
    assert relative_strength(pd.Series([10, 12]), pd.Series([100, 100])).iloc[0] == 1.0
