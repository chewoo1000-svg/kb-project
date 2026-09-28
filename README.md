# 금융 데이터랩 — 포트폴리오 데이터랩(F) × 시장 지표 브리핑(C)

> 가상 보유종목의 평가금액·손익을 SQL과 Pandas로 각각 계산해 교차검증하고(F), 같은 기간 시장 지표와 비교해 변동이 큰 구간을 찾아 AI 브리핑 문장으로 전달한다(C).

```
사용자 → 금융 데이터랩
          ├── F. 포트폴리오 데이터랩: 보유종목 평가금액 · 손익 · SQL ↔ Pandas 교차검증
          └── C. 시장 지표 브리핑:  주가지수(·금·배출권) · 변동구간 탐색 · AI 브리핑
```

설계 문서: [`docs/requirements.md`](docs/requirements.md) (요구사항·일정·리스크) · [`docs/api.md`](docs/api.md) (DB 스키마·서비스 인터페이스·API)

## 1. 문제 정의

- 데이터: `data/portfolio.csv`, `data/stock_prices.csv` (강사 제공), `data/market/index.csv` (금융위 API 또는 `collector.py` 대체 생성), 선택 `gold.csv`·`carbon.csv`
- 분석 질문
  1. 종목별 평가금액·손익률은 얼마이며, 상위/하위 3개는? (F)
  2. 포트폴리오와 시장지수의 일간 변화율을 비교했을 때 초과수익이 가장 컸던/부진했던 구간은? (F+C)
  3. 지수 급변일에 포트폴리오는 같은 방향으로 움직였는가, 어느 종목이 차이를 만들었는가? (F+C)
- 핵심 원칙: 같은 질문을 SQL과 Pandas로 각각 풀고, `outputs/`로 내보내 `tests/integration`이 비교한다.

## 2. 팀원별 역할 (독립 산출물 기준)

| # | 이름 | 역할 | 개인 산출물 |
|---|---|---|---|
| 1 | | SQL – 포트폴리오 (F) | `sql/portfolio.sql` → `outputs/sql_A_*.csv` |
| 2 | | SQL – 시계열·지수 비교 (F+C) | `sql/market.sql` → `outputs/sql_B_*.csv` |
| 3 | | Pandas – 포트폴리오 (F) | `backend/services/portfolio/calculator.py`, `notebooks/portfolio_analysis.ipynb` → `outputs/pandas_C_*.csv` |
| 4 | | Pandas – 시장 분석 (F+C) | `backend/services/market/analyzer.py`, `indicators.py`, `notebooks/market_analysis.ipynb` → `outputs/pandas_D_*.csv` |
| 5 | | 지표 수집 (C) | `backend/services/market/collector.py`, `notebooks/index_analysis.ipynb` → `data/market/*.csv`, `outputs/pandas_E_*.csv` |
| 6 | | 검증 | `tests/` (단위 + `integration/test_sql_vs_pandas.py`) → `outputs/validation_report.md` |
| 7 | | **리드** — 요구사항·DB/API 설계·Git 관리·통합 | `docs/*.md`, `backend/main.py`, `backend/api/*`, `services/ai/briefing.py`, `ai_log.md`, `result_report.md`, README |

리뷰 짝: 1↔3, 2↔4, 5↔6, 리드는 전체 PR. AI 사용 사례는 각자 `ai_log.md` 본인 섹션에 직접 커밋.

## 3. 실행 방법

```bash
pip install -r requirements.txt

python -m backend.services.market.collector        # 1) data/market/index.csv (API 실패 시 가상 지수)
python backend/utils/load_to_sqlite.py             # 2) data/*.csv → data/portfolio.db
python backend/utils/run_sql.py sql/portfolio.sql  # 3) SQL 실행 → outputs/sql_A_*.csv
python backend/utils/run_sql.py sql/market.sql     #    → outputs/sql_B_*.csv
jupyter notebook notebooks/                        # 4) portfolio / market / index 노트북 실행 → outputs/pandas_*.csv
python tests/integration/test_sql_vs_pandas.py     # 5) 교차검증 → outputs/validation_report.md
python -m backend.services.ai.briefing             # 6) 브리핑 문장 출력

# 선택
python -m pytest tests -q                          # 단위 테스트
uvicorn backend.main:app --reload                  # API  → http://127.0.0.1:8000/docs
streamlit run frontend/app.py                      # 화면
```

## 4. 핵심 결과

> `result_report.md` 참고. 요약 3줄:

- (결과 1)
- (결과 2)
- (결과 3)

## 5. 저장소 구조

```
docs/          requirements.md, api.md — 리드 설계 문서
data/          원본 CSV (수정 금지), market/ 지표 CSV
sql/           portfolio.sql (F), market.sql (F+C)
backend/
  services/    portfolio/ calculator·sql_compare, market/ collector·analyzer·indicators, ai/ briefing
  api/         FastAPI 라우터 (선택), main.py
  utils/       load_to_sqlite, run_sql
notebooks/     1인 1파일, services 함수를 import 해 결과·시각화
frontend/      app.py (Streamlit, 선택)
tests/         portfolio/ market/ 단위, integration/ SQL↔Pandas 교차검증 (채점용)
outputs/       결과 CSV·검증 리포트 (검증 입력 계약: docs/api.md §1)
```

## 6. Git 규칙 요약 (상세: `COMMIT_RULES.md`, `TEAM_GUIDE.md`)

- 각자 **개인 이름 브랜치**에서 작업, 작업 전 `git pull origin main`
- `main` 직접 push 금지 → 개인 브랜치에서 `main`으로 PR, 리뷰 1명 승인 후 리드가 머지
- 커밋 메시지: `[이름] type: 작업 내용` — `feat / fix / data / test / refactor / docs / chore`
- `.ipynb`는 1인 1파일, 커밋 전 output clear · `git push --force` 금지
