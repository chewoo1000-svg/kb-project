"""F API — docs/api.md §3"""
from fastapi import APIRouter
from ._common import read_csv, records

router = APIRouter(prefix="/portfolio", tags=["portfolio"])


@router.get("/valuation")
def valuation():
    return records(read_csv("pandas_C_valuation.csv"))


@router.get("/top-bottom")
def top_bottom(n: int = 3):
    df = read_csv("pandas_C_top_bottom.csv")
    return {"top": records(df[df["rank"] == "top"].head(n)), "bottom": records(df[df["rank"] == "bottom"].tail(n))}


@router.get("/daily")
def daily():
    return records(read_csv("pandas_D_daily_total.csv"))
