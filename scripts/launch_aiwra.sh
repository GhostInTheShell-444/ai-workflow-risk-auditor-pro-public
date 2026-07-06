#!/usr/bin/env bash
set -eu

SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
PROJECT_DIR="$(CDPATH= cd -- "$SCRIPT_DIR/.." && pwd)"
PYTHON="$PROJECT_DIR/.venv/bin/python"
APP="$PROJECT_DIR/app.py"
PORT="${AIWRA_PORT:-8501}"
STATE_HOME="${XDG_STATE_HOME:-$HOME/.local/state}"
LOG_DIR="$STATE_HOME/aiwra"
LOG_FILE="$LOG_DIR/aiwra-launch.log"
URL="http://127.0.0.1:$PORT"

fail() {
    printf '%s\n' "AIWRA launcher error: $*" >&2
    exit 1
}

case "$PORT" in
    *[!0-9]*|'') fail "AIWRA_PORT must be a numeric TCP port." ;;
esac
[ "$PORT" -ge 1 ] && [ "$PORT" -le 65535 ] || fail "AIWRA_PORT must be between 1 and 65535."

[ -f "$APP" ] || fail "app.py was not found in $PROJECT_DIR"
[ -x "$PYTHON" ] || fail "The virtual environment is missing. Create .venv and install requirements first."
"$PYTHON" -c "import streamlit" >/dev/null 2>&1 || fail "Streamlit is not installed in .venv. Run .venv/bin/python -m pip install -r requirements.txt"

mkdir -p "$LOG_DIR"
touch "$LOG_FILE"

if command -v xdg-open >/dev/null 2>&1; then
    (
        sleep 2
        xdg-open "$URL" >/dev/null 2>&1 || true
    ) &
fi

printf '%s\n' "Starting AI Workflow Risk Auditor Pro at $URL" >>"$LOG_FILE"
cd "$PROJECT_DIR"
exec "$PYTHON" -m streamlit run "$APP" \
    --server.address 127.0.0.1 \
    --server.port "$PORT" \
    --server.headless true \
    --browser.gatherUsageStats false >>"$LOG_FILE" 2>&1
