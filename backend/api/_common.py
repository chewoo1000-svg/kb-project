from pathlib import Path
from fastapi import HTTPException
import pandas as pd

OUT = Path(__file__).resolve().parents[2] / "outputs"


def read_csv(name: str) -> pd.DataFrame:
    p = OUT / name
    if not p.exists():
        raise HTTPException(404, f"outputs/{name} not found — run notebooks first")
    return pd.read_csv(p)


def records(df: pd.DataFrame):
    return df.astype(object).where(df.notna(), None).to_dict(orient="records")
