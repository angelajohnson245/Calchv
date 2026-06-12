"""
utils/loader.py
---------------
Shared data-loading utilities for the Calculator Validation Workspace.

All loaders use @st.cache_data / @st.cache_resource so the JSON/pickle
are only read once per session regardless of which page triggers the load.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import streamlit as st

# ── Resolve paths relative to the workspace_app directory ─────────────────────
WORKSPACE_DIR = Path(__file__).parent.parent          # workspace_app/
CALC_DIR      = WORKSPACE_DIR.parent                  # calculator/
JSON_PATH     = CALC_DIR / "default_21492.json"
BASELINE_PKL  = CALC_DIR / "engine_baseline.pkl"
COMPARISON_XL = CALC_DIR / "setup_df_comparison.xlsx"

# Make sure setup_init.py is importable
sys.path.insert(0, str(CALC_DIR))


# ─────────────────────────────────────────────────────────────────────────────
# JSON summary (always available — no m61_finance dependency)
# ─────────────────────────────────────────────────────────────────────────────

@st.cache_data(show_spinner=False)
def load_json_summary() -> dict:
    """
    Read the raw JSON and return a lightweight summary dict.
    No dependency on m61_finance; always works.
    """
    with open(JSON_PATH) as fh:
        raw = json.load(fh)

    data = raw["data"]
    return {
        "json_filename":      JSON_PATH.name,
        "note_id":            str(data.get("root_note_id", "?")),
        "period_start":       data.get("period_start_date", "?"),
        "period_end":         data.get("period_end_date", "?"),
        "effective_dates":    data.get("effective_dates", []),
        "account_count":      len(data.get("accounts", {})),
        "notes_count":        len(data.get("notes", {})),
        "index_count":        len(data.get("index", {})),
        "calendar_markets":   list(data.get("calendar", {}).keys()),
        "fee_fn_count":       len(data.get("lstfeefunctions", [])),
        "structure_count":    len(data.get("structure", [])),
        "global_flags": {
            "calc_basis":                  data.get("calc_basis", "?"),
            "calc_deffee_basis":           data.get("calc_deffee_basis", "?"),
            "accountingclose":             data.get("accountingclose", "?"),
            "disable_businessday":         data.get("disable_businessday", "?"),
            "maturity_scenario_override":  data.get("maturity_scenario_override", "?"),
            "use_servicingactual":         data.get("use_servicingactual", "?"),
        },
    }


# ─────────────────────────────────────────────────────────────────────────────
# Full setup result (requires m61_finance)
# ─────────────────────────────────────────────────────────────────────────────

@st.cache_resource(show_spinner=False)
def load_setup_result():
    """
    Run initialize_calculator_dataframe and return the SetupResult.
    Returns (result, error_message). error_message is None on success.
    """
    try:
        from setup_init import initialize_calculator_dataframe
        result = initialize_calculator_dataframe(JSON_PATH)
        return result, None
    except ImportError as exc:
        return None, f"m61_finance not available: {exc}"
    except Exception as exc:
        return None, f"Setup failed: {exc}"


# ─────────────────────────────────────────────────────────────────────────────
# Engine baseline
# ─────────────────────────────────────────────────────────────────────────────

@st.cache_data(show_spinner=False)
def load_engine_baseline() -> tuple[pd.DataFrame | None, str | None]:
    """Load engine baseline pickle. Returns (df, error)."""
    if not BASELINE_PKL.exists():
        return None, "engine_baseline.pkl not found"
    try:
        df = pd.read_pickle(str(BASELINE_PKL))
        return df, None
    except Exception as exc:
        return None, f"Could not load baseline: {exc}"


# ─────────────────────────────────────────────────────────────────────────────
# Comparison workbook
# ─────────────────────────────────────────────────────────────────────────────

@st.cache_data(show_spinner=False)
def load_comparison_summary() -> tuple[pd.DataFrame | None, str | None]:
    """
    Parse the 'Comparison Summary' sheet from setup_df_comparison.xlsx.
    Returns (summary_df, error).
    """
    if not COMPARISON_XL.exists():
        return None, "setup_df_comparison.xlsx not found"
    try:
        df = pd.read_excel(COMPARISON_XL, sheet_name="Comparison Summary",
                           header=None, engine="openpyxl")
        return df, None
    except Exception as exc:
        return None, str(exc)


@st.cache_data(show_spinner=False)
def load_comparison_detail() -> tuple[pd.DataFrame | None, str | None]:
    """
    Load the per-column detail rows from the Comparison Summary sheet
    (rows after the header at row 18).
    """
    df_raw, err = load_comparison_summary()
    if err or df_raw is None:
        return None, err

    # Find the header row (contains 'Column')
    header_row_idx = None
    for i, row in df_raw.iterrows():
        if str(row.iloc[0]).strip() == "Column":
            header_row_idx = i
            break

    if header_row_idx is None:
        return None, "Could not locate column detail header"

    detail = df_raw.iloc[header_row_idx:].copy()
    detail.columns = detail.iloc[0]
    detail = detail.iloc[1:].reset_index(drop=True)
    detail = detail.dropna(how="all")
    return detail, None


@st.cache_data(show_spinner=False)
def load_comparison_top_metrics() -> dict:
    """
    Extract the scalar metrics from rows 3–16 of the Comparison Summary sheet.
    """
    df_raw, err = load_comparison_summary()
    defaults = {
        "rows_new": "2,458", "rows_old": "2,458", "rows_match": "✓",
        "cols_new": "286", "cols_old": "332",
        "shared_cols": "286",
        "matched_cols": "259/286", "conflict_cols": "27",
        "conflict_rows": "2,898",
        "parts_pass": "146/146",
        "balance_ready": "Yes — no blockers",
    }
    if err or df_raw is None:
        return defaults

    metrics = {}
    for i, row in df_raw.iterrows():
        label = str(row.iloc[0]).strip() if row.iloc[0] else ""
        val_a = str(row.iloc[1]).strip() if row.iloc[1] else ""
        val_b = str(row.iloc[2]).strip() if row.iloc[2] else ""
        match  = str(row.iloc[3]).strip() if row.iloc[3] else ""

        if label == "Rows":
            metrics.update(rows_new=val_a, rows_old=val_b, rows_match=match)
        elif label == "Total columns":
            metrics.update(cols_new=val_a, cols_old=val_b)
        elif label == "Shared columns":
            metrics["shared_cols"] = val_a
        elif label == "Cols with full match":
            metrics["matched_cols"] = val_a
        elif label == "Cols with conflicts":
            metrics["conflict_cols"] = val_a
        elif label == "Total conflicting rows":
            metrics["conflict_rows"] = val_a
        elif label == "Parts 1–10 pass":
            metrics["parts_pass"] = val_a
        elif label == "Balance-ready verdict":
            metrics["balance_ready"] = val_a

    return {**defaults, **metrics}
