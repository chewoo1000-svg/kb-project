# result_report.md — 최종 분석 결과와 근거

> 모든 수치는 `outputs/`의 CSV 파일명과 함께 적는다. 근거 파일이 없는 주장은 넣지 않는다.

## 1. 데이터 개요

| 파일 | 행 수 | 기간 | 종목 수 | 비고 (결측/중복) |
|---|---|---|---|---|
| portfolio.csv | | – | | |
| stock_prices.csv | | ~ | | |
| market_index.csv | | ~ | (지수명) | API / 대체 생성 여부 |

## 2. 질문 1 — 종목별 평가금액·손익률

- 계산식: 평가금액 = 보유수량 × 최신 종가, 손익률 = (평가금액 − 매입금액) / 매입금액
- SQL 결과: `outputs/sql_A_valuation.csv`
- Pandas 결과: `outputs/pandas_C_valuation.csv`
- 검증: `tests/integration/test_sql_vs_pandas.py` — 일치 여부 (허용 오차: )

| 순위 | 종목 | 평가금액 | 손익률 |
|---|---|---|---|
| 상위 1 | | | |
| 상위 2 | | | |
| 상위 3 | | | |
| 하위 1 | | | |
| 하위 2 | | | |
| 하위 3 | | | |

해석 (데이터로 확인 가능한 것만):

## 3. 질문 2 — 포트폴리오 vs 시장지수: 초과수익이 가장 컸던/부진했던 구간

- 사용 지수: (코스피 / SYNTH_KOSPI — 대체 생성 시 이유 기재)
- SQL 결과: `outputs/sql_B_vs_index.csv`
- Pandas 결과: `outputs/pandas_D_vs_index.csv`
- 검증 결과: (port_pct / index_pct / excess_pct 일치 여부, 거래일 정합)

| 구분 | 일자 | 포트폴리오 변화율 | 지수 변화율 | 초과수익률 |
|---|---|---|---|---|
| 최대 초과 1 | | | | |
| 최대 초과 2 | | | | |
| 최소 초과 1 | | | | |
| 최소 초과 2 | | | | |

해석:

## 4. 질문 3 — 지수 급변일에 포트폴리오는 어떻게 움직였고, 어느 종목이 차이를 만들었나

- SQL 결과: `outputs/sql_B_index_shock_days.csv`, `outputs/sql_B_contribution.csv`
- Pandas 결과: `outputs/pandas_D_index_shock_days.csv`
- 지수 자체 분석: `outputs/pandas_E_index_summary.csv`

| 일자 | 지수 변화율 | 포트폴리오 변화율 | 방향 | 기여도 최대 종목 |
|---|---|---|---|---|
| | | | | |

해석:

## 5. 한계 및 확인하지 못한 것

- (예) stock_prices.csv에 거래정지일이 있어 해당 일자는 전일 종가로 대체함
- (예) 배당·수수료는 데이터에 없어 손익에 미반영
- (예) 지수 API 발급 불가로 stock_prices 평균 기반 가상 지수(SYNTH_KOSPI)를 사용함 — 실제 시장과 다름

## 6. AI 브리핑 (`python -m backend.services.ai.briefing` 출력을 붙이고, 수치가 위 표와 일치하는지 확인)

> 

## 7. 결론 3줄

1.
2.
3.
