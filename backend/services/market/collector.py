"""
fetch_index.py — 시장지수(market_index.csv) 확보. 담당: 5번
1) 금융위원회 '지수시세정보' API 시도 (data.go.kr 키 필요, 환경변수 DATA_GO_KR_KEY)
2) 실패 시 stock_prices.csv 전 종목 평균으로 '가상 시장지수' 생성 (SYNTH_KOSPI)

실행: python -m backend.services.market.collector            # data/market_index.csv 생성
컬럼: trade_date, index_name, close_value
"""
import os
import sys
from pathlib import Path
import pandas as pd

DATA = Path(__file__).resolve().parents[3] / "data"
OUT = DATA / "market" / "index.csv"


def from_api(start: str, end: str) -> pd.DataFrame | None:
    key = os.getenv("DATA_GO_KR_KEY")
    if not key:
        print("[api] DATA_GO_KR_KEY 없음 → 대체 경로")
        return None
    try:
        import requests
        url = "https://apis.data.go.kr/1160100/service/GetMarketIndexInfoService/getStockMarketIndex"
        rows = []
        for name in ["코스피", "코스닥"]:
            r = requests.get(url, params={
                "serviceKey": key, "resultType": "json", "numOfRows": 1000,
                "beginBasDt": start, "endBasDt": end, "idxNm": name}, timeout=15)
            r.raise_for_status()
            items = r.json()["response"]["body"]["items"]["item"]
            for it in items:
                rows.append((pd.to_datetime(it["basDt"]).date(), it["idxNm"], float(it["clpr"])))
        df = pd.DataFrame(rows, columns=["trade_date", "index_name", "close_value"])
        print(f"[api] {len(df)} rows")
        return df if len(df) else None
    except Exception as e:
        print(f"[api] 실패: {e} → 대체 경로")
        return None


def synthetic(sp: pd.DataFrame) -> pd.DataFrame:
    """전 종목 종가 평균을 첫날=1000 기준으로 정규화한 가상 지수."""
    m = sp.groupby("trade_date")["close_price"].mean().sort_index()
    idx = (m / m.iloc[0] * 1000).round(2)
    df = idx.reset_index().rename(columns={"close_price": "close_value"})
    df["index_name"] = "SYNTH_KOSPI"
    print(f"[synthetic] {len(df)} rows (stock_prices 평균 기반)")
    return df[["trade_date", "index_name", "close_value"]]


def main():
    sp = pd.read_csv(DATA / "stock_prices.csv")
    sp.columns = sp.columns.str.strip().str.lower()
    sp["trade_date"] = pd.to_datetime(sp["trade_date"]).dt.date
    start, end = min(sp["trade_date"]).strftime("%Y%m%d"), max(sp["trade_date"]).strftime("%Y%m%d")
    df = from_api(start, end)
    if df is None:
        df = synthetic(sp)
    df.to_csv(OUT, index=False)
    print(f"→ {OUT.name} 저장. index_name: {sorted(df.index_name.unique())}")


if __name__ == "__main__":
    sys.exit(main())
