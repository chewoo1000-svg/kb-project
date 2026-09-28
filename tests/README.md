# tests

| 폴더 | 내용 | 실행 |
|---|---|---|
| `portfolio/` | calculator 단위 테스트 | `python -m pytest tests -q` |
| `market/` | indicators 단위 테스트 | 〃 |
| `integration/test_sql_vs_pandas.py` | **채점용 교차검증** — outputs/의 SQL 결과 vs Pandas 결과, 거래일 정합 | `python tests/integration/test_sql_vs_pandas.py` |

integration 스크립트는 pytest 없이 단독 실행되며 FAIL 시 exit 1. 결과는 `outputs/validation_report.md`.
