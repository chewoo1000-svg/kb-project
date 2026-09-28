"""C API — docs/api.md §3"""
from fastapi import APIRouter
from ._common import read_csv, records, OUT
from backend.services.ai.briefing import build_facts, render

router = APIRouter(tags=["market"])


@router.get("/market/summary")
def summary():
    return records(read_csv("pandas_E_index_summary.csv"))


@router.get("/market/vs-index")
def vs_index():
    return records(read_csv("pandas_D_vs_index.csv"))


@router.get("/market/shock-days")
def shock_days(n: int = 5):
    return records(read_csv("pandas_D_index_shock_days.csv").head(n))


@router.get("/briefing")
def briefing():
    facts = build_facts()
    return {"text": render(facts), "facts": facts}


@router.get("/validation")
def validation():
    p = OUT / "validation_report.md"
    text = p.read_text(encoding="utf-8") if p.exists() else ""
    return {"pass": "FAIL" not in text and "PASS" in text, "report": text}
