#!/usr/bin/env bash
set -eu

SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
PROJECT_DIR="$(CDPATH= cd -- "$SCRIPT_DIR/.." && pwd)"
DESTINATION="${1:-$HOME/Desktop/AI Workflow Risk Auditor Pro.command}"
ESCAPED_PROJECT=$(printf '%s' "$PROJECT_DIR" | sed "s/'/'\\\\''/g")

[ -f "$PROJECT_DIR/app.py" ] || {
    printf '%s\n' "app.py was not found in $PROJECT_DIR" >&2
    exit 1
}
[ -x "$PROJECT_DIR/.venv/bin/python" ] || {
    printf '%s\n' "Create .venv and install requirements before creating the launcher." >&2
    exit 1
}
"$PROJECT_DIR/.venv/bin/python" -c "import streamlit" >/dev/null 2>&1 || {
    printf '%s\n' "Streamlit is unavailable in .venv. Install requirements first." >&2
    exit 1
}

{
    printf '%s\n' '#!/usr/bin/env bash'
    printf '%s\n' 'set -eu'
    printf '%s\n' "PROJECT_DIR='$ESCAPED_PROJECT'"
    printf '%s\n' 'LOG_DIR="${HOME}/Library/Logs/AIWRA"'
    printf '%s\n' 'LOG_FILE="${LOG_DIR}/aiwra-launch.log"'
    printf '%s\n' 'mkdir -p "$LOG_DIR"'
    printf '%s\n' '(sleep 2; open "http://127.0.0.1:8501") &'
    printf '%s\n' 'cd "$PROJECT_DIR"'
    printf '%s\n' 'exec "$PROJECT_DIR/.venv/bin/python" -m streamlit run "$PROJECT_DIR/app.py" --server.address 127.0.0.1 --server.port 8501 --browser.gatherUsageStats false >>"$LOG_FILE" 2>&1'
} >"$DESTINATION"

chmod 755 "$DESTINATION"
printf '%s\n' "Created $DESTINATION"
printf '%s\n' "This helper has not been tested on macOS in this repository pass."
printf '%s\n' "Remove it with: rm \"$DESTINATION\""
