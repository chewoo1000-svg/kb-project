"""선택 과제 — FastAPI. outputs/*.csv 를 읽어 반환만 한다 (계산 없음). docs/api.md §3
실행: pip install fastapi uvicorn && uvicorn backend.main:app --reload
"""
from fastapi import FastAPI
from backend.api import portfolio, market

app = FastAPI(title="금융 데이터랩 API", version="1.0")
app.include_router(portfolio.router)
app.include_router(market.router)


@app.get("/health")
def health():
    return {"status": "ok"}
