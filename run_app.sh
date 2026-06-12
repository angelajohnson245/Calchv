#!/bin/bash
# Run the Calculator Validation Workspace
# Usage: bash workspace_app/run_app.sh
# or from the calculator/ directory:
#   cd /path/to/calculator && bash workspace_app/run_app.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CALC_DIR="$(dirname "$SCRIPT_DIR")"

echo "=================================================="
echo " M61 Calculator Validation Workspace"
echo " Prototype — Management Review"
echo "=================================================="
echo ""
echo " App directory : $SCRIPT_DIR"
echo " Calculator dir: $CALC_DIR"
echo ""

# Check streamlit
if ! python3 -m streamlit --version &>/dev/null; then
    echo "Installing streamlit..."
    python3 -m pip install streamlit plotly openpyxl --break-system-packages -q
fi

echo " Starting Streamlit..."
echo " Open http://localhost:8501 in your browser."
echo ""

cd "$SCRIPT_DIR"
python3 -m streamlit run app.py \
    --server.headless false \
    --browser.gatherUsageStats false \
    --theme.base light \
    --theme.primaryColor "#1565c0" \
    --theme.backgroundColor "#ffffff" \
    --theme.secondaryBackgroundColor "#f0f4f8" \
    --theme.textColor "#1a1a2e"
