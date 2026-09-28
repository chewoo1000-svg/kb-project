"""
run_sql.py — SQL 파일을 SQLite에서 실행하고 결과를 outputs/ 에 CSV로 내보낸다.
sqlite3 CLI가 없어도 동작한다. (Oracle 사용 시엔 SQL Developer에서 export해도 됨)

SQL 파일 안에서 내보낼 쿼리 바로 위에 아래 주석을 붙인다:
    -- @export: sql_A_valuation.csv

실행:
    python backend/utils/load_to_sqlite.py            # 먼저 1회
    python backend/utils/run_sql.py sql/portfolio.sql
    python backend/utils/run_sql.py sql/market.sql
"""
import re
import sqlite3
import sys
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
DB = ROOT / "data" / "portfolio.db"
OUT = ROOT / "outputs"


def split_statements(text: str):
    """세미콜론 기준으로 문장을 나누고, 각 문장 앞 주석에서 @export 파일명을 뽑는다."""
    stmts = []
    for chunk in text.split(";"):
        m = re.search(r"--\s*@export:\s*(\S+)", chunk)
        body = "\n".join(l for l in chunk.splitlines() if not l.strip().startswith("--")).strip()
        if body:
            stmts.append((m.group(1) if m else None, body))
    return stmts


def main(path: str):
    OUT.mkdir(exist_ok=True)
    con = sqlite3.connect(DB)
    for export, sql in split_statements(Path(path).read_text(encoding="utf-8")):
        try:
            df = pd.read_sql_query(sql, con)
        except Exception as e:  # 실패한 문장은 알려주고 계속 진행
            print(f"[ERROR] {e}\n  --> {sql[:80]}...")
            continue
        if export:
            df.to_csv(OUT / export, index=False)
            print(f"[export] {export}  ({len(df)} rows)")
        else:
            print(f"[ok] {sql.splitlines()[0][:60]}...  ({len(df)} rows)")
    con.close()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit("usage: python backend/utils/run_sql.py sql/portfolio.sql")
    main(sys.argv[1])
