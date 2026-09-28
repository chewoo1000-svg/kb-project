-- ============================================================
-- queries_A.sql — SQL 담당 1: 보유/평가/손익
-- 담당: (이름)   브랜치: <본인 github id>
-- 결과 내보내기: outputs/sql_A_valuation.csv, outputs/sql_A_top_bottom.csv
-- 컬럼명은 실제 CSV를 확인한 뒤 수정한다.
-- ============================================================

-- [A-0] 데이터 확인: 행 수, 결측, 중복
SELECT COUNT(*) AS n_rows FROM portfolio;
SELECT COUNT(*) AS n_rows FROM stock_prices;
SELECT ticker, COUNT(*) AS cnt FROM portfolio GROUP BY ticker HAVING COUNT(*) > 1;

-- [A-1] 종목별 최신 종가
-- Oracle: ROW_NUMBER() OVER (...) 또는 MAX(date) 서브쿼리
WITH latest AS (
    SELECT ticker, MAX(trade_date) AS last_date
    FROM stock_prices
    GROUP BY ticker
)
SELECT p.ticker, p.close_price AS last_close, p.trade_date
FROM stock_prices p
JOIN latest l ON p.ticker = l.ticker AND p.trade_date = l.last_date;

-- [A-2] 종목별 평가금액 / 매입금액 / 손익 / 손익률
-- @export: sql_A_valuation.csv
WITH latest AS (
    SELECT ticker, MAX(trade_date) AS last_date
    FROM stock_prices GROUP BY ticker
),
last_price AS (
    SELECT p.ticker, p.close_price
    FROM stock_prices p
    JOIN latest l ON p.ticker = l.ticker AND p.trade_date = l.last_date
)
SELECT
    pf.ticker,
    pf.quantity,
    pf.buy_price,
    lp.close_price,
    pf.quantity * pf.buy_price              AS cost_amount,
    pf.quantity * lp.close_price            AS eval_amount,
    pf.quantity * (lp.close_price - pf.buy_price)                          AS pnl,
    ROUND((lp.close_price - pf.buy_price) / pf.buy_price * 100, 2)         AS pnl_pct
FROM portfolio pf
JOIN last_price lp ON pf.ticker = lp.ticker
ORDER BY pnl_pct DESC;

-- [A-3] 손익률 상위 3 / 하위 3  (Oracle: LIMIT 대신 FETCH FIRST 3 ROWS ONLY)
-- @export: sql_A_top_bottom.csv
WITH latest AS (
    SELECT ticker, MAX(trade_date) AS last_date FROM stock_prices GROUP BY ticker
),
val AS (
    SELECT pf.ticker,
           pf.quantity * p.close_price AS eval_amount,
           ROUND((p.close_price - pf.buy_price) / pf.buy_price * 100, 2) AS pnl_pct
    FROM portfolio pf
    JOIN latest l ON pf.ticker = l.ticker
    JOIN stock_prices p ON p.ticker = l.ticker AND p.trade_date = l.last_date
),
ranked AS (
    SELECT ticker, eval_amount, pnl_pct,
           ROW_NUMBER() OVER (ORDER BY pnl_pct DESC) AS rn_desc,
           ROW_NUMBER() OVER (ORDER BY pnl_pct ASC)  AS rn_asc
    FROM val
)
SELECT ticker, eval_amount, pnl_pct,
       CASE WHEN rn_desc <= 3 THEN 'top' ELSE 'bottom' END AS rank
FROM ranked
WHERE rn_desc <= 3 OR rn_asc <= 3
ORDER BY pnl_pct DESC;

-- [A-4] 종목 비중 (평가금액 / 전체 평가금액) — SUM() OVER () 윈도우 함수
-- @export: sql_A_weight.csv
WITH latest AS (
    SELECT ticker, MAX(trade_date) AS last_date FROM stock_prices GROUP BY ticker
),
val AS (
    SELECT pf.ticker, pf.quantity * p.close_price AS eval_amount
    FROM portfolio pf
    JOIN latest l ON pf.ticker = l.ticker
    JOIN stock_prices p ON p.ticker = l.ticker AND p.trade_date = l.last_date
)
SELECT ticker, eval_amount,
       ROUND(eval_amount * 100.0 / SUM(eval_amount) OVER (), 2) AS weight_pct
FROM val
ORDER BY weight_pct DESC;
