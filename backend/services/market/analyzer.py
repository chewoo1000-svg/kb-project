"""C. 시장 지표 분석 — docs/api.md §2 인터페이스."""
from pathlib import Path
import numpy as np
import pandas as pd
from .indicators import daily_returns, excess_return, relative_strength


def load_market(root: Path, name: str = "index.csv") -> pd.DataFrame:
    df = pd.read_csv(root / "data" / "market" / name)
    df.columns = df.columns.str.strip().str.lower()
    df["trade_date"] = pd.to_datetime(df["trade_date"])
    return df


def summarize(mi: pd.DataFrame) -> pd.DataFrame:
    piv = mi.pivot(index="trade_date", columns="index_name", values="close_value").sort_index()
    ret = piv.pct_change() * 100
    return pd.DataFrame({"mean": piv.mean(), "max": piv.max(), "min": piv.min(),
                         "max_date": piv.idxmax(), "min_date": piv.idxmin(),
                         "daily_vol": ret.std().round(3)}).reset_index()


def vs_index(daily: pd.DataFrame, mi: pd.DataFrame, index_name: str | None = None) -> pd.DataFrame:
    index_name = index_name or sorted(mi["index_name"].unique())[0]   # SQL [B-6]과 동일: 첫 지수
    idx = mi[mi["index_name"] == index_name][["trade_date", "close_value"]]
    vs = daily[["trade_date", "total_eval"]].merge(idx, on="trade_date", how="inner")
    vs["port_pct"] = daily_returns(vs["total_eval"])
    vs["index_pct"] = daily_returns(vs["close_value"])
    vs["excess_pct"] = excess_return(vs["port_pct"], vs["index_pct"])
    vs["rel_strength"] = relative_strength(vs["total_eval"], vs["close_value"])
    return vs


def shock_days(vs: pd.DataFrame, n: int = 5) -> pd.DataFrame:
    s = vs.dropna(subset=["index_pct"]).reindex(vs["index_pct"].abs().sort_values(ascending=False).index).head(n).copy()
    s["direction"] = np.where((s.index_pct > 0) == (s.port_pct > 0), "same", "opposite")
    return s[["trade_date", "index_pct", "port_pct", "direction"]]


def contribution(sp: pd.DataFrame, pf: pd.DataFrame, dates) -> pd.DataFrame:
    m = sp.merge(pf[["ticker", "quantity"]], on="ticker").sort_values(["ticker", "trade_date"])
    m["price_diff"] = m.groupby("ticker")["close_price"].diff()
    m["pnl_contribution"] = (m["quantity"] * m["price_diff"]).round(2)
    return m[m["trade_date"].isin(pd.to_datetime(list(dates)))][["trade_date", "ticker", "pnl_contribution"]] \
            .sort_values(["trade_date", "pnl_contribution"], ascending=[True, False])
