"""
load_to_sqlite.py — data/*.csv 를 data/portfolio.db (SQLite) 로 적재
Oracle 환경이 막히거나 로컬에서 SQL을 돌려볼 때 사용.

실행: python backend/utils/load_to_sqlite.py
이후:  python backend/utils/run_sql.py sql/portfolio.sql
"""
import sqlite3
from pathlib import Path
import pandas as pd

DATA = Path(__file__).resolve().parents[2] / "data"
db = sqlite3.connect(DATA / "portfolio.db")
TABLES = {  # 파일 → 테이블명 (docs/api.md 의 DB 스키마와 일치)
    DATA / "portfolio.csv": "portfolio",
    DATA / "stock_prices.csv": "stock_prices",
    DATA / "market" / "index.csv": "market_index",
    DATA / "market" / "gold.csv": "market_gold",
    DATA / "market" / "carbon.csv": "market_carbon",
}
for csv, table in TABLES.items():
    if not csv.exists():
        print(f"(없음) {csv.relative_to(DATA.parent)} → {table} 건너뜀"); continue
    df = pd.read_csv(csv)
    df.columns = df.columns.str.strip().str.lower()
    df.to_sql(table, db, if_exists="replace", index=False)
    print(f"{csv.name} → 테이블 {table} ({len(df)} rows)")
db.close()
