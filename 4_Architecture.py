"""
Architecture Diagram
====================
Visual overview of the M61 calculator conversion:
JSON → Setup → Balance → Interest → Fees pipeline,
m61_finance dependency map, and engine retirement roadmap.
"""

import sys
from datetime import date
from pathlib import Path

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
    page_title="Architecture · M61 Calculator",
    page_icon="🏗️",
    layout="wide",
)

with st.sidebar:
    st.markdown("## 🏦 M61 Calculator")
    st.markdown("**Validation Workspace**")
    st.caption("Prototype — Read Only")
    st.divider()
    st.caption(f"M61 Product Conversion · {date.today().year}")

# ── Header ────────────────────────────────────────────────────────────────────
st.title("🏗️ Architecture Diagram")
st.markdown(
    "System architecture for the M61 CRE calculator conversion: "
    "pipeline flow, m61_finance library dependencies, and engine retirement roadmap."
)
st.divider()

# ─────────────────────────────────────────────────────────────────────────────
# Diagram 1: Pipeline Flow  (JSON → Setup → Balance → Interest → Fees)
# ─────────────────────────────────────────────────────────────────────────────
st.subheader("Calculator Pipeline")

PIPELINE_HTML = """
<style>
.pipeline-wrap {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    padding: 24px 12px;
    overflow-x: auto;
}
.pipeline-row {
    display: flex;
    align-items: center;
    flex-wrap: nowrap;
    gap: 0;
}
.pipe-node {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    min-width: 130px;
    padding: 14px 10px;
    border-radius: 10px;
    text-align: center;
    font-size: 0.82em;
    font-weight: 600;
    box-shadow: 0 2px 6px rgba(0,0,0,0.12);
    position: relative;
}
.pipe-node .status-badge {
    margin-top: 6px;
    font-size: 0.72em;
    font-weight: 400;
    border-radius: 20px;
    padding: 2px 8px;
    color: white;
}
.pipe-arrow {
    font-size: 1.6em;
    color: #888;
    margin: 0 4px;
    flex-shrink: 0;
}
/* node colours */
.n-json    { background:#fff3e0; border:2px solid #fb8c00; color:#e65100; }
.n-setup   { background:#e8f5e9; border:2px solid #43a047; color:#1b5e20; }
.n-balance { background:#e3f2fd; border:2px solid #1e88e5; color:#0d47a1; }
.n-interest{ background:#fce4ec; border:2px solid #e91e63; color:#880e4f; }
.n-fees    { background:#f3e5f5; border:2px solid #8e24aa; color:#4a148c; }
.n-output  { background:#fafafa; border:2px solid #546e7a; color:#263238; }
.badge-done    { background:#28a745; }
.badge-next    { background:#007bff; }
.badge-planned { background:#6c757d; }
/* detail boxes below */
.pipe-detail {
    display: flex;
    gap: 12px;
    margin-top: 24px;
    flex-wrap: wrap;
}
.detail-card {
    flex: 1;
    min-width: 140px;
    border-radius: 8px;
    padding: 12px;
    font-size: 0.78em;
    line-height: 1.5;
}
.dc-json    { background:#fff8f0; border-left:4px solid #fb8c00; }
.dc-setup   { background:#f0faf0; border-left:4px solid #43a047; }
.dc-balance { background:#f0f6ff; border-left:4px solid #1e88e5; }
.dc-interest{ background:#fff0f5; border-left:4px solid #e91e63; }
.dc-fees    { background:#faf0ff; border-left:4px solid #8e24aa; }
</style>
<div class="pipeline-wrap">
  <div class="pipeline-row">

    <div class="pipe-node n-json">
      📄<br>default_21492<br>.json
      <span class="status-badge badge-done">Source</span>
    </div>

    <span class="pipe-arrow">→</span>

    <div class="pipe-node n-setup">
      ⚙️<br>Setup / Init<br>(Parts 1–10)
      <span class="status-badge badge-done">✅ Complete</span>
    </div>

    <span class="pipe-arrow">→</span>

    <div class="pipe-node n-balance">
      💰<br>Balance
      <span class="status-badge badge-next">⏳ Next</span>
    </div>

    <span class="pipe-arrow">→</span>

    <div class="pipe-node n-interest">
      📈<br>Interest
      <span class="status-badge badge-planned">⏳ Planned</span>
    </div>

    <span class="pipe-arrow">→</span>

    <div class="pipe-node n-fees">
      💸<br>Fees
      <span class="status-badge badge-planned">⏳ Planned</span>
    </div>

    <span class="pipe-arrow">→</span>

    <div class="pipe-node n-output">
      📊<br>Output<br>DataFrame
      <span class="status-badge badge-planned">Target</span>
    </div>

  </div>

  <div class="pipe-detail">
    <div class="detail-card dc-json">
      <strong>JSON Input</strong><br>
      • 280 account columns<br>
      • 35 effective dates<br>
      • Rate / spread tables<br>
      • Calendar + index data<br>
      • 11 fee functions
    </div>
    <div class="detail-card dc-setup">
      <strong>Setup Output</strong><br>
      • 2,458 × 286 DataFrame<br>
      • Accrual date columns (8)<br>
      • Rate tables (step-fn)<br>
      • Index + fee lookups<br>
      • 146/146 checks ✅
    </div>
    <div class="detail-card dc-balance">
      <strong>Balance (Next)</strong><br>
      • Funding / repayment<br>
      • Scheduled principal<br>
      • PIK accumulation<br>
      • endbal / trueloanbal<br>
      • Commitment tracking
    </div>
    <div class="detail-card dc-interest">
      <strong>Interest (Planned)</strong><br>
      • Index rate lookups<br>
      • All-in coupon rate<br>
      • Daily accrual<br>
      • PIK interest split<br>
      • Stub interest
    </div>
    <div class="detail-card dc-fees">
      <strong>Fees (Planned)</strong><br>
      • Unused fee calc<br>
      • GAAP basis amort<br>
      • Exit fee logic<br>
      • Level-yield fee<br>
      • Fee function dispatch
    </div>
  </div>
</div>
"""

st.components.v1.html(PIPELINE_HTML, height=360, scrolling=False)

st.divider()

# ─────────────────────────────────────────────────────────────────────────────
# Diagram 2: m61_finance Dependency Map
# ─────────────────────────────────────────────────────────────────────────────
st.subheader("m61_finance Dependency Map")

FINANCE_HTML = """
<style>
.dep-wrap {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    padding: 20px 12px;
}
.dep-grid {
    display: grid;
    grid-template-columns: 200px 60px 1fr;
    gap: 16px;
    align-items: start;
}
.dep-lib {
    background: linear-gradient(135deg, #1565c0, #283593);
    color: white;
    border-radius: 10px;
    padding: 16px;
    text-align: center;
    font-weight: bold;
    font-size: 0.95em;
    box-shadow: 0 3px 8px rgba(0,0,0,0.2);
}
.dep-lib small { display:block; font-weight:400; font-size:0.75em; margin-top:4px; opacity:0.85; }
.dep-arrows {
    display: flex;
    flex-direction: column;
    justify-content: space-around;
    align-items: center;
    color: #888;
    font-size: 1.3em;
    padding-top: 8px;
    height: 100%;
}
.dep-consumers {
    display: flex;
    flex-direction: column;
    gap: 10px;
}
.dep-consumer {
    border-radius: 8px;
    padding: 10px 14px;
    font-size: 0.82em;
}
.dc-setup2  { background:#e8f5e9; border-left:4px solid #43a047; }
.dc-balance2{ background:#e3f2fd; border-left:4px solid #1e88e5; }
.dc-interest2{background:#fce4ec; border-left:4px solid #e91e63; }
.dep-consumer strong { color:#333; }
.dep-consumer .fn { color:#555; font-family:monospace; font-size:0.9em; }
</style>
<div class="dep-wrap">
  <div class="dep-grid">
    <div class="dep-lib">
      📦 m61_finance<br>
      <small>m61_finance.cre.dates<br>m61_finance.cre.rates</small>
    </div>
    <div class="dep-arrows">
      →<br>→<br>→<br>→<br>→<br>→
    </div>
    <div class="dep-consumers">
      <div class="dep-consumer dc-setup2">
        <strong>Setup (✅ Active)</strong><br>
        <span class="fn">get_holiday_calendar()</span> — resolve holiday lists per eff date<br>
        <span class="fn">get_holiday_adjusted_dates()</span> — compute matdt_holadj<br>
        <span class="fn">get_periodend_date()</span> — compute per-period loop_until<br>
        <span class="fn">get_accrual_dates()</span> — populate month/periodend/pmtdt/term/indexrefdt<br>
        <span class="fn">get_rates()</span> — rate/spread/floor/cap step-function lookup<br>
        <span class="fn">get_pikrates()</span> — PIK rate table with start+end date args
      </div>
      <div class="dep-consumer dc-balance2">
        <strong>Balance (⏳ Planned)</strong><br>
        <span class="fn">index_table.asof(date)</span> — step-function index rate lookup<br>
        <span class="fn">apply_precision_rounding()</span> — engine-compatible rounding
      </div>
      <div class="dep-consumer dc-interest2">
        <strong>Interest (⏳ Planned)</strong><br>
        <span class="fn">m61_finance.cre.rates.get_rates()</span> — reset period rate lookup<br>
        <span class="fn">coupon / basis helpers</span> — from m61_finance.cre
      </div>
    </div>
  </div>
</div>
"""
st.components.v1.html(FINANCE_HTML, height=320, scrolling=False)

st.divider()

# ─────────────────────────────────────────────────────────────────────────────
# Diagram 3: Engine Retirement Roadmap
# ─────────────────────────────────────────────────────────────────────────────
st.subheader("Engine Retirement Roadmap")

ROADMAP_HTML = """
<style>
.roadmap-wrap {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    padding: 20px 12px;
}
.roadmap-timeline {
    position: relative;
    padding-left: 32px;
}
.roadmap-timeline::before {
    content: '';
    position: absolute;
    left: 10px;
    top: 0;
    bottom: 0;
    width: 3px;
    background: linear-gradient(#28a745, #007bff, #fd7e14, #8e24aa, #dc3545);
    border-radius: 3px;
}
.roadmap-item {
    position: relative;
    margin-bottom: 20px;
    padding: 12px 16px;
    border-radius: 8px;
    font-size: 0.84em;
}
.roadmap-item::before {
    content: '';
    position: absolute;
    left: -27px;
    top: 14px;
    width: 14px;
    height: 14px;
    border-radius: 50%;
    border: 2px solid white;
}
.ri-done   { background:#e8f5e9; border-left:4px solid #28a745; }
.ri-done::before   { background:#28a745; }
.ri-next   { background:#e3f2fd; border-left:4px solid #007bff; }
.ri-next::before   { background:#007bff; }
.ri-plan1  { background:#fff3e0; border-left:4px solid #fd7e14; }
.ri-plan1::before  { background:#fd7e14; }
.ri-plan2  { background:#f3e5f5; border-left:4px solid #8e24aa; }
.ri-plan2::before  { background:#8e24aa; }
.ri-retire { background:#fce4ec; border-left:4px solid #dc3545; }
.ri-retire::before { background:#dc3545; }
.ri-status { font-weight:700; font-size:0.95em; margin-bottom:3px; }
</style>
<div class="roadmap-wrap">
  <div class="roadmap-timeline">
    <div class="roadmap-item ri-done">
      <div class="ri-status">✅ Current — Setup / Init Complete</div>
      Parts 1–10 of setup conversion validated (146/146 checks).
      Python <code>setup_init.py</code> replaces all JSON setup rules.
      <code>m61_finance</code> integrated for accrual dates and rate tables.
    </div>
    <div class="roadmap-item ri-next">
      <div class="ri-status">⏳ Next — Balance Module</div>
      Implement <code>balance.py</code> using setup_init output.
      Validate funding, principal, and PIK accumulation against engine baseline.
      Target: identical output to within precision rounding.
    </div>
    <div class="roadmap-item ri-plan1">
      <div class="ri-status">⏳ Later — Interest Module</div>
      Implement <code>interest.py</code>.
      Use <code>m61_finance.cre.rates</code> for index lookups.
      Cover cash interest, PIK interest, stub periods.
    </div>
    <div class="roadmap-item ri-plan2">
      <div class="ri-status">⏳ Later — Fees + Integration</div>
      Implement <code>fees.py</code> using fee_function_lookup.
      Full end-to-end integration test: Setup → Balance → Interest → Fees.
      Regression suite against engine baseline for all test notes.
    </div>
    <div class="roadmap-item ri-retire">
      <div class="ri-status">🏁 Future — Engine Retirement / Product Integration</div>
      JSON rule engine decommissioned.
      All M61 CRE notes calculated via Python stack.
      <code>m61_finance</code> becomes the sole financial library dependency.
    </div>
  </div>
</div>
"""
st.components.v1.html(ROADMAP_HTML, height=480, scrolling=False)

st.divider()

# ─────────────────────────────────────────────────────────────────────────────
# Key Design Decisions table
# ─────────────────────────────────────────────────────────────────────────────
st.subheader("Key Architectural Decisions")

import pandas as pd

decisions = pd.DataFrame({
    "Decision": [
        "Single JSON read per session",
        "m61_finance for all date/rate logic",
        "setup_init exposes SetupResult dataclass",
        "index_table as pd.Series (asof)",
        "fee_function_lookup as {int: dict}",
        "Precision rounding in Balance/Interest",
        "6 engine-written extras in df",
        "Step-function via merge_asof fallback",
    ],
    "Rationale": [
        "Matches engine: parse once, mutate df per eff date",
        "Avoid duplicating financial math; finance lib is the authority",
        "Clean public API — Balance/Interest import one object",
        "O(log n) asof() lookup matches engine index rate retrieval",
        "O(1) fee function dispatch vs O(n) list scan",
        "Setup writes raw values; rounding applied at final write time",
        "Balance JSON rules reference these via @df.<field>",
        "Fills every date in window, not just record start dates",
    ],
    "Status": [
        "✅ Implemented",
        "✅ Implemented",
        "✅ Implemented",
        "✅ Implemented",
        "✅ Implemented",
        "⏳ Balance/Interest",
        "✅ Implemented",
        "✅ Implemented",
    ],
})
st.dataframe(decisions, hide_index=True, use_container_width=True)

st.markdown("---")
st.caption("Architecture Diagram · M61 Calculator Validation Workspace · Read Only")
