"""
Calculator Validation Workspace — Home / Calculator Summary
===========================================================
Entry point for the Streamlit multi-page app.
Run with:  streamlit run workspace_app/app.py
"""

import sys
from datetime import date
from pathlib import Path

import pandas as pd
import streamlit as st

# ── Path setup ────────────────────────────────────────────────────────────────
APP_DIR  = Path(__file__).parent
CALC_DIR = APP_DIR.parent
sys.path.insert(0, str(CALC_DIR))
sys.path.insert(0, str(APP_DIR))

from utils.loader import (
    load_json_summary,
    load_setup_result,
    load_comparison_top_metrics,
)

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Calculator Validation Workspace",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Sidebar branding ──────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🏦 M61 Calculator")
    st.markdown("**Validation Workspace**")
    st.caption("Prototype — Read Only")
    st.divider()
    st.caption(f"M61 Product Conversion · {date.today().year}")

# ── Page header ───────────────────────────────────────────────────────────────
st.title("📋 Calculator Summary")
st.divider()

# ── Load data ─────────────────────────────────────────────────────────────────
with st.spinner("Loading calculator data…"):
    summary = load_json_summary()
    metrics = load_comparison_top_metrics()

result, setup_err = load_setup_result()

if setup_err:
    st.warning(
        f"⚠️ **Demo mode** — setup engine offline (`{setup_err}`). "
        "Displaying static reference data from comparison workbook.",
        icon="⚠️",
    )
    setup_status = "⚠️ Demo Mode"
    setup_color  = "orange"
else:
    setup_status = "✅ Complete"
    setup_color  = "green"

# ── Key metrics row ───────────────────────────────────────────────────────────
st.subheader("Calculator File")

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("JSON File",              summary["json_filename"])
c2.metric("Note ID",                summary["note_id"])
c3.metric("Effective Dates",        len(summary["effective_dates"]))
c4.metric("Account Columns",        summary["account_count"])
c5.metric("Setup Validation",       setup_status)

st.divider()

# ── Period & configuration ────────────────────────────────────────────────────
left, right = st.columns(2)

with left:
    st.subheader("Calculation Window")
    eff_dates = summary["effective_dates"]
    window_df = pd.DataFrame({
        "Field":  ["Period Start Date", "Period End Date",
                   "First Effective Date", "Last Effective Date",
                   "Total Effective Dates"],
        "Value": [
            summary["period_start"],
            summary["period_end"],
            eff_dates[0]  if eff_dates else "—",
            eff_dates[-1] if eff_dates else "—",
            str(len(eff_dates)),
        ],
    })
    st.dataframe(window_df, hide_index=True, use_container_width=True)

with right:
    st.subheader("Global Flags")
    flags = summary["global_flags"]
    flag_df = pd.DataFrame({
        "Flag":  list(flags.keys()),
        "Value": [str(v) for v in flags.values()],
    })
    st.dataframe(flag_df, hide_index=True, use_container_width=True)

st.divider()

# ── Setup validation status ───────────────────────────────────────────────────
st.subheader("Setup Validation Status")

col_a, col_b, col_c, col_d = st.columns(4)
col_a.metric("Parts Passed",         metrics.get("parts_pass", "146/146"))
col_b.metric("Matched Columns",      metrics.get("matched_cols", "259/286"))
col_c.metric("Columns with Diffs",   metrics.get("conflict_cols", "27"))
col_d.metric("Balance-Ready",        metrics.get("balance_ready", "Yes"))

st.divider()

# ── Data objects summary ──────────────────────────────────────────────────────
st.subheader("Data Objects")

obj_col1, obj_col2, obj_col3 = st.columns(3)

with obj_col1:
    st.markdown("**Index Rates**")
    st.dataframe(
        pd.DataFrame({
            "Index":  summary.get("index_count", 1) * ["1m Term SOFR"],
            "Points": ["See Setup Viewer"],
        }),
        hide_index=True, use_container_width=True,
    )

with obj_col2:
    st.markdown("**Holiday Calendars**")
    st.dataframe(
        pd.DataFrame({
            "Market": summary["calendar_markets"],
        }),
        hide_index=True, use_container_width=True,
    )

with obj_col3:
    st.markdown("**Fee Functions**")
    st.dataframe(
        pd.DataFrame({
            "Stat":  ["Total Fee Functions", "Structure Notes"],
            "Count": [str(summary["fee_fn_count"]), str(summary["structure_count"])],
        }),
        hide_index=True, use_container_width=True,
    )

st.divider()

# ── Effective date list ───────────────────────────────────────────────────────
with st.expander("📅 All Effective Dates", expanded=False):
    eff_dates = summary["effective_dates"]
    n_cols = 5
    rows   = [eff_dates[i:i+n_cols] for i in range(0, len(eff_dates), n_cols)]
    ed_df  = pd.DataFrame(rows, columns=[f"Date {i+1}" for i in range(n_cols)])
    st.dataframe(ed_df, hide_index=True, use_container_width=True)
    st.caption(f"{len(eff_dates)} effective dates · First: {eff_dates[0]}  Last: {eff_dates[-1]}")

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("---")
st.caption(
    "M61 Calculator Conversion Prototype · Setup Phase Complete · "
    "Balance / Interest / Fees — Not Started · Read-Only Demo"
)
