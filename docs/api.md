# DB 스키마 · API 설계

작성: 리드 · 버전 1.0

## 1. DB 스키마 (SQLite `data/portfolio.db`, Oracle 동일 구조)

`backend/utils/load_to_sqlite.py`가 `data/*.csv`를 아래 테이블로 적재한다. 컬럼명은 CSV 헤더를 소문자로 정규화한 값이며, 강사 CSV 헤더가 다르면 이 문서 기준으로 코드 쪽을 맞춘다.

```
portfolio                  보유종목 (F 입력)
├─ ticker        TEXT  PK   종목코드
├─ quantity      REAL       보유수량
└─ buy_price     REAL       매입단가

stock_prices               일자별 종가 (F 입력)
├─ trade_date    DATE  PK₁  거래일 (YYYY-MM-DD)
├─ ticker        TEXT  PK₂  → portfolio.ticker
└─ close_price   REAL       종가

market_index               시장지수 (C 입력)  ← data/market/index.csv
├─ trade_date    DATE  PK₁
├─ index_name    TEXT  PK₂  '코스피' | '코스닥' | 'SYNTH_KOSPI'(대체 생성)
└─ close_value   REAL

market_gold / market_carbon   (선택)  ← data/market/gold.csv, carbon.csv
├─ trade_date    DATE  PK
├─ index_name    TEXT       'GOLD_1KG' | 'KAU'
└─ close_value   REAL
```

관계: `stock_prices.ticker → portfolio.ticker` (N:1). 시장 테이블은 `trade_date`로만 F 결과와 JOIN한다.

### 파생 뷰 (SQL 파일 안의 CTE로 구현, 실제 뷰는 만들지 않음)

| 이름 | 정의 | 원천 SQL |
|---|---|---|
| `latest_price` | ticker별 MAX(trade_date)의 close_price | `sql/portfolio.sql` [A-1] |
| `valuation` | quantity×close_price, 손익, 손익률, 비중 | [A-2]~[A-4] |
| `daily_total` | trade_date별 SUM(quantity×close_price) | `sql/market.sql` [B-1] |
| `vs_index` | daily_total ⨝ market_index, 변화율·초과수익률 | [B-6] |

### 결과 파일 계약 (`outputs/`, 검증 스크립트가 읽는 인터페이스)

| 파일 | 키 | 비교 컬럼 | 생성 |
|---|---|---|---|
| `sql_A_valuation.csv` / `pandas_C_valuation.csv` | ticker | eval_amount, pnl_pct | SQL 1 / Pandas 3 |
| `sql_B_daily_total.csv` / `pandas_D_daily_total.csv` | trade_date | total_eval | SQL 2 / Pandas 4 |
| `sql_B_vs_index.csv` / `pandas_D_vs_index.csv` | trade_date | port_pct, index_pct, excess_pct | SQL 2 / Pandas 4 |

**같은 키·같은 컬럼명**을 지켜야 `tests/integration/test_sql_vs_pandas.py`가 자동으로 비교한다. 컬럼을 추가하는 건 자유, 이름을 바꾸면 리드에게 먼저 알린다.

## 2. 내부 서비스 인터페이스 (`backend/services/`)

노트북·API·브리핑이 모두 같은 함수를 호출한다. 노트북에 계산을 직접 쓰지 말고 여기 함수를 import해서 결과를 보여준다.

```python
# backend/services/portfolio/calculator.py
load_data(root) -> (portfolio: DataFrame, prices: DataFrame)
valuation(portfolio, prices) -> DataFrame   # ticker, quantity, buy_price, close_price,
                                            # cost_amount, eval_amount, pnl, pnl_pct, weight_pct
top_bottom(val, n=3) -> DataFrame           # + rank ('top'|'bottom')
daily_total(portfolio, prices) -> DataFrame # trade_date, total_eval, diff_amt, diff_pct

# backend/services/portfolio/sql_compare.py
compare(sql_csv, pandas_csv, keys, cols, tol=0.01) -> dict  # {pass: bool, max_diff: {...}, missing_keys: [...]}

# backend/services/market/collector.py
fetch_index(start, end) -> DataFrame | None  # 금융위 API
synthetic_index(prices) -> DataFrame        # 대체 생성
main() -> data/market/index.csv

# backend/services/market/indicators.py
daily_returns(df, value_col) -> Series
excess_return(port_pct, index_pct) -> Series
drawdown(series) -> Series
relative_strength(port, index) -> Series

# backend/services/market/analyzer.py
summarize(market_df) -> DataFrame           # index_name별 mean/max/min/vol/max_date/min_date
vs_index(daily, index_df, index_name) -> DataFrame   # trade_date, total_eval, close_value, port_pct, index_pct, excess_pct
shock_days(vs, n=5) -> DataFrame            # |index_pct| 상위 n, direction same/opposite
contribution(prices, portfolio, dates) -> DataFrame  # 급변일 종목별 pnl_contribution

# backend/services/ai/briefing.py
build_facts(outputs_dir) -> dict            # outputs/*.csv 에서 수치 추출
render(facts) -> str                        # 규칙 기반 한국어 브리핑 (LLM 없이도 동작)
```

## 3. HTTP API (선택 · FastAPI · `backend/main.py`)

핵심 분석이 03:00까지 끝난 뒤에만 구현한다. 모든 응답은 `outputs/` CSV를 읽어 반환하며 계산을 다시 하지 않는다.

| Method | Path | 응답 | 원천 파일 |
|---|---|---|---|
| GET | `/health` | `{"status":"ok"}` | — |
| GET | `/portfolio/valuation` | `[{ticker, quantity, close_price, eval_amount, pnl, pnl_pct, weight_pct}]` | pandas_C_valuation.csv |
| GET | `/portfolio/top-bottom?n=3` | `{top:[...], bottom:[...]}` | pandas_C_top_bottom.csv |
| GET | `/portfolio/daily` | `[{trade_date, total_eval, diff_pct}]` | pandas_D_daily_total.csv |
| GET | `/market/summary` | `[{index_name, mean, max, min, daily_vol}]` | pandas_E_index_summary.csv |
| GET | `/market/vs-index` | `[{trade_date, port_pct, index_pct, excess_pct}]` | pandas_D_vs_index.csv |
| GET | `/market/shock-days?n=5` | `[{trade_date, index_pct, port_pct, direction}]` | pandas_D_index_shock_days.csv |
| GET | `/briefing` | `{"text": "...", "facts": {...}}` | briefing.render() |
| GET | `/validation` | `{"pass": true, "pairs": [...]}` | validation_report.md |

에러: 원천 파일이 없으면 `404 {"detail": "outputs/<file> not found — run notebooks first"}`.

실행: `uvicorn backend.main:app --reload` → http://127.0.0.1:8000/docs

## 4. 프론트엔드 (선택)

`frontend/`는 위 API를 호출하는 화면 2개(`pages/portfolio`, `pages/market`)를 목표로 하되, 4시간 안에는 **Streamlit 한 파일**(`frontend/app.py`)로 대체하는 것을 권장한다. `st.dataframe`으로 valuation·vs_index 표, `st.line_chart`로 상대강도, 상단에 `/briefing` 텍스트.

## 5. 변경 관리

- 스키마·결과 파일 계약(§1)을 바꾸려면 리드에게 PR 코멘트로 먼저 제안 → 승인 후 이 문서와 코드를 같은 PR에서 수정.
- 컬럼 추가는 자유, 이름 변경·삭제는 승인 필요.
