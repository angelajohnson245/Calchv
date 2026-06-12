"""
Module Progress Tracker
========================
Tracks conversion progress across Setup, Balance, Interest, and Fees modules.
"""

import sys
from datetime import date
from pathlib import Path

import pandas as pd
import streamlit as st

try:
    import plotly.graph_objects as go
    PLOTLY_OK = True
except ImportError:
    PLOTLY_OK = False

APP_DIR  = Path(__file__).resolve().parent.parent
CALC_DIR = APP_DIR.parent
_ROOT = APP_DIR
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Module Progress · M61 Calculator",
    page_icon="📊",
    layout="wide",
)

with st.sidebar:
    st.markdown("## 🏦 M61 Calculator")
    st.markdown("**Validation Workspace**")
    st.caption("Prototype — Read Only")
    st.divider()
    st.caption(f"M61 Product Conversion · {date.today().year}")

# ── Header ────────────────────────────────────────────────────────────────────
st.title("📊 Module Progress Tracker")
st.markdown(
    "Conversion progress for each calculator module. "
    "Setup is fully validated and balance-ready. Remaining modules follow in sequence below."
)
st.divider()

# ── Module definitions ────────────────────────────────────────────────────────
MODULES = [
    {
        "name":     "Setup / Initialization",
        "status":   "Complete",
        "icon":     "✅",
        "pct":      100,
        "color":    "#28a745",
        "parts":    "Parts 1–10",
        "checks":   "146/146",
        "files":    "setup_init.py",
        "notes":    (
            "All 10 conversion plan parts validated. "
            "280 account columns initialized. "
            "35 effective dates processed. "
            "m61_finance integrated for accrual dates, rate tables, holiday calendars. "
            "Balance-ready: no blocking issues."
        ),
        "deliverables": [
            "✅ JSON parsing and section extraction (Part 1)",
            "✅ DataFrame skeleton with account defaults (Part 2)",
            "✅ Default value and reset behavior (Part 3)",
            "✅ Effective date filtering (Part 4)",
            "✅ Note scalar loading — read_dict (Part 5)",
            "✅ Config / calendar / index store (Part 6)",
            "✅ Pre-Balance column completeness (Part 7)",
            "✅ Engine behavior fidelity (Part 8)",
            "✅ Helper and lookup object quality (Part 9)",
            "✅ Execution order indicators (Part 10)",
        ],
    },
    {
        "name":     "Balance",
        "status":   "Not Started",
        "icon":     "⏳",
        "pct":      0,
        "color":    "#6c757d",
        "parts":    "Next",
        "checks":   "—",
        "files":    "balance.py (planned)",
        "notes":    (
            "Setup output is balance-ready. "
            "Key inputs available: effectivedate, loanterm, periodend, pmtdt, "
            "rate_val, spread_val, index_floor_val. "
            "Blockers resolved: m61_finance available, all 8 accrual columns populated."
        ),
        "deliverables": [
            "⏳ Funding and repayment logic",
            "⏳ Scheduled principal calculation",
            "⏳ PIK balance accumulation",
            "⏳ Balance forward-fill per effective date",
            "⏳ Commitment column integration",
        ],
    },
    {
        "name":     "Interest",
        "status":   "Not Started",
        "icon":     "⏳",
        "pct":      0,
        "color":    "#6c757d",
        "parts":    "Later",
        "checks":   "—",
        "files":    "interest.py (planned)",
        "notes":    (
            "Depends on Balance output. "
            "Will use m61_finance.cre.rates for index lookups. "
            "Key fields: indexrate, allincouponrate, dailyint, periodint."
        ),
        "deliverables": [
            "⏳ Index rate retrieval via index_table.asof()",
            "⏳ All-in coupon rate calculation",
            "⏳ Daily interest accrual",
            "⏳ PIK interest separation",
            "⏳ Stub interest handling",
        ],
    },
    {
        "name":     "Fees",
        "status":   "Not Started",
        "icon":     "⏳",
        "pct":      0,
        "color":    "#6c757d",
        "parts":    "Later",
        "checks":   "—",
        "files":    "fees.py (planned)",
        "notes":    (
            "Uses fee_function_lookup (11 functions indexed by FunctionNameID). "
            "Key fields: unusedfee_pct, dailyunusedfee, gaapbasis, feeamort."
        ),
        "deliverables": [
            "⏳ Unused fee calculation",
            "⏳ GAAP basis amortization",
            "⏳ Exit fee logic",
            "⏳ Level-yield fee",
            "⏳ Fee function dispatch via lookup",
        ],
    },
]

# ── Overall progress bar ──────────────────────────────────────────────────────
overall_pct = sum(m["pct"] for m in MODULES) / len(MODULES)
st.subheader("Overall Conversion Progress")

prog_col1, prog_col2 = st.columns([3, 1])
with prog_col1:
    st.progress(int(overall_pct) / 100)
with prog_col2:
    st.metric("Progress", f"{overall_pct:.0f}%", delta="Setup Complete")

st.divider()

# ── Module status cards ───────────────────────────────────────────────────────
st.subheader("Module Status")

card_cols = st.columns(len(MODULES))

for col, m in zip(card_cols, MODULES):
    with col:
        st.markdown(
            f"""
            <div style="
                border: 2px solid {m['color']};
                border-radius: 10px;
                padding: 16px;
                text-align: center;
                background: {'#f0fff4' if m['status'] == 'Complete' else '#f8f9fa'};
            ">
                <div style="font-size: 2em; margin-bottom: 4px;">{m['icon']}</div>
                <div style="font-weight: bold; font-size: 1.05em; color: {m['color']}">
                    {m['name']}
                </div>
                <div style="font-size: 0.85em; margin-top: 4px; color: #444;">
                    {m['status']}
                </div>
                <div style="
                    background: {m['color']};
                    color: white;
                    border-radius: 20px;
                    padding: 2px 10px;
                    margin-top: 8px;
                    font-size: 0.8em;
                ">
                    {m['pct']}%
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.caption(m["parts"])

st.divider()

# ── Status roadmap ────────────────────────────────────────────────────────────
if PLOTLY_OK:
    st.subheader("Conversion Roadmap")

    phases = [
        ("Setup / Initialization", "Current — Setup / Init Complete", "#28a745"),
        ("Balance", "Next — Balance Module", "#007bff"),
        ("Interest", "Later — Interest Module", "#fd7e14"),
        ("Fees + Integration", "Later — Fees + Integration", "#6f42c1"),
        ("Engine Retirement / Product Integration", "Future — Engine Retirement / Product Integration", "#dc3545"),
    ]

    fig = go.Figure()
    for i, (task, status_label, color) in enumerate(phases):
        fig.add_trace(go.Bar(
            name=task,
            x=[1],
            y=[task],
            base=[i],
            orientation="h",
            marker_color=color,
            marker_opacity=0.85,
            text=f"  {status_label}",
            textposition="inside",
            insidetextanchor="start",
            showlegend=False,
        ))

    fig.update_layout(
        barmode="overlay",
        xaxis=dict(
            tickmode="array",
            tickvals=[i + 0.5 for i in range(len(phases))],
            ticktext=[status for _, status, _ in phases],
            title="Phase",
            showgrid=False,
            range=[0, len(phases)],
        ),
        yaxis=dict(
            title="",
            autorange="reversed",
        ),
        plot_bgcolor="white",
        paper_bgcolor="white",
        height=260,
        margin=dict(t=20, b=40, l=180, r=20),
        font=dict(size=11),
    )
    st.plotly_chart(fig, use_container_width=True)
    st.divider()

# ── Module detail accordions ──────────────────────────────────────────────────
st.subheader("Module Detail")

for m in MODULES:
    with st.expander(f"{m['icon']} {m['name']} — {m['status']}", expanded=(m["status"] == "Complete")):
        d1, d2 = st.columns(2)

        with d1:
            st.markdown(f"**Status:** {m['icon']} {m['status']}")
            st.markdown(f"**Validation checks:** {m['checks']}")
            st.markdown(f"**File:** `{m['files']}`")
            st.markdown(f"**Notes:** {m['notes']}")

        with d2:
            st.markdown("**Deliverables:**")
            for item in m["deliverables"]:
                st.markdown(f"- {item}")

        if m["pct"] > 0:
            st.progress(m["pct"] / 100, text=f"{m['pct']}% complete")

st.divider()

# ── Upcoming milestones ───────────────────────────────────────────────────────
st.subheader("Upcoming Milestones")

milestones = pd.DataFrame({
    "Milestone": [
        "Begin Balance module development",
        "Balance unit tests vs engine baseline",
        "Begin Interest module development",
        "Begin Fees module development",
        "Full integration test (Setup → Fees)",
        "Engine retirement planning",
    ],
    "Phase": [
        "Next — Balance Module",
        "Next — Balance Module",
        "Later — Interest Module",
        "Later — Fees + Integration",
        "Later — Fees + Integration",
        "Future — Engine Retirement / Product Integration",
    ],
    "Depends On": [
        "Setup ✅",
        "Balance",
        "Balance",
        "Interest",
        "Fees",
        "Full Integration",
    ],
    "Status": [
        "🟢 Ready to start",
        "🔵 Planned",
        "🔵 Planned",
        "🔵 Planned",
        "🔵 Planned",
        "🔵 Planned",
    ],
})
st.dataframe(milestones, hide_index=True, use_container_width=True)

st.markdown("---")
st.caption("Module Progress Tracker · M61 Calculator Validation Workspace · Read Only")
