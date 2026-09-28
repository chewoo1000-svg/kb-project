"""선택 과제 — Streamlit 한 파일 화면. docs/api.md §4
실행: pip install streamlit && streamlit run frontend/app.py
"""
from pathlib import Path
import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs"
import sys; sys.path.insert(0, str(ROOT))
from backend.services.ai.briefing import build_facts, render


def load(name):
    p = OUT / name
    return pd.read_csv(p) if p.exists() else None

st.title("금융 데이터랩 — 포트폴리오 × 시장 지표")
st.subheader("AI 브리핑")
st.write(render(build_facts()))

tab1, tab2 = st.tabs(["F. 포트폴리오", "C. 시장 지표"])
with tab1:
    val = load("pandas_C_valuation.csv")
    if val is not None:
        st.dataframe(val); st.bar_chart(val.set_index("ticker")["pnl_pct"])
    daily = load("pandas_D_daily_total.csv")
    if daily is not None:
        st.line_chart(daily.set_index("trade_date")["total_eval"])
with tab2:
    vs = load("pandas_D_vs_index.csv")
    if vs is not None:
        st.line_chart(vs.set_index("trade_date")[["port_pct", "index_pct"]])
        st.line_chart(vs.set_index("trade_date")["rel_strength"])
    sh = load("pandas_D_index_shock_days.csv")
    if sh is not None:
        st.dataframe(sh)
