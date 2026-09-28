"""F. 포트폴리오 계산 — docs/api.md §2 인터페이스. 노트북·API·테스트가 공통으로 사용."""
from pathlib import Path
import pandas as pd


def load_data(root: Path):
    pf = pd.read_csv(root / "data" / "portfolio.csv")
    sp = pd.read_csv(root / "data" / "stock_prices.csv")
    pf.columns, sp.columns = pf.columns.str.strip().str.lower(), sp.columns.str.strip().str.lower()
    sp["trade_date"] = pd.to_datetime(sp["trade_date"])
    return pf, sp


def valuation(pf: pd.DataFrame, sp: pd.DataFrame) -> pd.DataFrame:
    last = sp.sort_values("trade_date").groupby("ticker").tail(1)[["ticker", "close_price"]]
    v = pf.merge(last, on="ticker")
    v["cost_amount"] = v["quantity"] * v["buy_price"]
    v["eval_amount"] = v["quantity"] * v["close_price"]
    v["pnl"] = v["eval_amount"] - v["cost_amount"]
    v["pnl_pct"] = ((v["close_price"] - v["buy_price"]) / v["buy_price"] * 100).round(2)
    v["weight_pct"] = (v["eval_amount"] / v["eval_amount"].sum() * 100).round(2)
    return v.sort_values("pnl_pct", ascending=False).reset_index(drop=True)


def top_bottom(val: pd.DataFrame, n: int = 3) -> pd.DataFrame:
    return pd.concat([val.head(n).assign(rank="top"), val.tail(n).assign(rank="bottom")])


def daily_total(pf: pd.DataFrame, sp: pd.DataFrame) -> pd.DataFrame:
    m = sp.merge(pf[["ticker", "quantity"]], on="ticker")
    m["eval"] = m["quantity"] * m["close_price"]
    d = m.groupby("trade_date", as_index=False)["eval"].sum().rename(columns={"eval": "total_eval"})
    d["diff_amt"] = d["total_eval"].diff()
    d["diff_pct"] = (d["total_eval"].pct_change() * 100).round(2)
    return d
