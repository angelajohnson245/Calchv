"""
Setup Output Viewer
===================
Displays the initialized setup DataFrame with search and filter controls.
Shows key setup fields: effectivedate, loanterm, rate tables, commitments.
"""

import sys
from datetime import date
from pathlib import Path

import pandas as pd
import streamlit as st

_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from utils.loader import load_setup_result, load_json_summary

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Setup Output Viewer · M61 Calculator",
    page_icon="🔍",
    layout="wide",
)

with st.sidebar:
    st.markdown("## 🏦 M61 Calculator")
    st.markdown("**Validation Workspace**")
    st.caption("Prototype — Read Only")
    st.divider()
    st.caption(f"M61 Product Conversion · {date.today().year}")

# ── Header ────────────────────────────────────────────────────────────────────
st.title("🔍 Setup Output Viewer")
st.markdown(
    "Inspect the initialized setup DataFrame produced by `setup_init.py`. "
    "Use the column selector and search filters below."
)
st.divider()

# ── Key column groups ─────────────────────────────────────────────────────────
KEY_GROUPS = {
    "Identity":        ["Date", "Note", "effectivedate"],
    "Loan Terms":      ["loanterm", "ioterm", "amterm", "clsdt", "initmatdt",
                        "initaccenddt", "initpmtdt"],
    "Accrual Dates":   ["month", "periodstart", "periodend", "pmtdt",
                        "pmtdtnotadj", "contractualpmtdt", "term", "indexrefdt"],
    "Rate Tables":     ["rate_val", "rate_adj_factor", "rate_intcalcdays",
                        "spread_val", "spread_adj_factor",
                        "index_floor_val", "index_cap_val",
                        "coupon_floor_val"],
    "Commitments":     ["totalcmt", "noteadjustedtotalcommitment", "initfunding"],
    "Global Flags":    ["precision", "roundmethod", "leaddays",
                        "paydatebusiessdaylag"],
    "IO / Amort":      ["io_term_end_date", "amort_rate_val", "amort_spread_val",
                        "amort_floor_val"],
}

# ── Load data ─────────────────────────────────────────────────────────────────
with st.spinner("Initializing setup DataFrame…"):
    result, err = load_setup_result()

if err or result is None:
    st.warning(
        f"⚠️ **Demo mode** — setup engine offline (`{err}`). "
        "Loading from comparison workbook fallback.",
        icon="⚠️",
    )
    # Fallback: load from the xlsx comparison workbook
    try:
        fallback_df = pd.read_excel(
            CALC_DIR / "setup_df_comparison.xlsx",
            sheet_name="Setup DF (New)",
            engine="openpyxl",
        )
        df = fallback_df
        source_label = "Source: setup_df_comparison.xlsx (cached)"
    except Exception as xl_err:
        st.error(f"Could not load fallback data: {xl_err}")
        st.stop()
else:
    df = result.df.reset_index(drop=True)
    source_label = "Source: setup_init.py (live)"

st.caption(source_label)

# ── Metrics row ───────────────────────────────────────────────────────────────
m1, m2, m3, m4 = st.columns(4)
m1.metric("Rows",    f"{len(df):,}")
m2.metric("Columns", f"{df.shape[1]:,}")
m3.metric("Note ID", str(df["Note"].iloc[0]) if "Note" in df.columns else "—")
m4.metric(
    "Date Range",
    f"{pd.Timestamp(df['Date'].min()).strftime('%m/%d/%Y') if 'Date' in df.columns else '—'}"
    f" → "
    f"{pd.Timestamp(df['Date'].max()).strftime('%m/%d/%Y') if 'Date' in df.columns else '—'}",
)

st.divider()

# ── Column selector ───────────────────────────────────────────────────────────
st.subheader("Column Selection")

col_left, col_right = st.columns([1, 3])

with col_left:
    group_choice = st.radio(
        "Quick group",
        options=["All"] + list(KEY_GROUPS.keys()),
        index=1,
    )

with col_right:
    if group_choice == "All":
        default_cols = list(df.columns[:20])
    else:
        default_cols = [c for c in KEY_GROUPS[group_choice] if c in df.columns]

    selected_cols = st.multiselect(
        "Columns to display",
        options=list(df.columns),
        default=default_cols,
        help="Add or remove columns. Choose a group on the left to pre-select a set.",
    )

if not selected_cols:
    st.info("Select at least one column above.")
    st.stop()

# ── Date range filter ─────────────────────────────────────────────────────────
st.subheader("Filters")
f1, f2, f3 = st.columns(3)

df_display = df.copy()

if "Date" in df.columns:
    all_dates = pd.to_datetime(df["Date"], errors="coerce").dropna()
    min_date  = all_dates.min().date()
    max_date  = all_dates.max().date()

    with f1:
        date_from = st.date_input("Date from", value=min_date,
                                  min_value=min_date, max_value=max_date)
    with f2:
        date_to   = st.date_input("Date to",   value=max_date,
                                  min_value=min_date, max_value=max_date)

    mask = (
        pd.to_datetime(df_display["Date"], errors="coerce").dt.date >= date_from
    ) & (
        pd.to_datetime(df_display["Date"], errors="coerce").dt.date <= date_to
    )
    df_display = df_display.loc[mask]

with f3:
    text_search = st.text_input("Search value (scans selected columns)", "")

if text_search:
    mask_text = df_display[selected_cols].apply(
        lambda col: col.astype(str).str.contains(text_search, case=False, na=False)
    ).any(axis=1)
    df_display = df_display.loc[mask_text]

# ── Results ───────────────────────────────────────────────────────────────────
st.divider()
st.subheader(f"DataFrame — {len(df_display):,} rows × {len(selected_cols)} columns")

view_df = df_display[selected_cols].copy()

# Format Timestamp columns for readability
for col in view_df.columns:
    try:
        if pd.api.types.is_datetime64_any_dtype(view_df[col]):
            view_df[col] = pd.to_datetime(view_df[col]).dt.strftime("%Y-%m-%d")
        elif view_df[col].dtype == object:
            sample = view_df[col].dropna().iloc[0] if not view_df[col].dropna().empty else None
            if hasattr(sample, 'strftime'):
                view_df[col] = view_df[col].apply(
                    lambda v: v.strftime("%Y-%m-%d") if hasattr(v, 'strftime') else v
                )
    except Exception:
        pass

st.dataframe(
    view_df,
    use_container_width=True,
    hide_index=True,
    height=480,
)

# ── Non-null summary for selected columns ─────────────────────────────────────
with st.expander("📊 Column fill rates (selected columns)", expanded=False):
    fill_data = []
    for col in selected_cols:
        total   = len(df[col])
        non_null = int(df[col].notna().sum())
        pct     = non_null / total * 100 if total else 0
        fill_data.append({
            "Column":     col,
            "Non-null":   f"{non_null:,}",
            "Total":      f"{total:,}",
            "Fill %":     f"{pct:.1f}%",
            "Status":     "✓ Full" if pct == 100 else ("⚠ Partial" if pct > 0 else "✗ Empty"),
        })
    st.dataframe(pd.DataFrame(fill_data), hide_index=True, use_container_width=True)

st.markdown("---")
st.caption("Setup Output Viewer · M61 Calculator Validation Workspace · Read Only")
