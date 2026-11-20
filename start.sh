#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

echo "=============================================================="
echo "WJC GLOBAL — JARVIS COMMAND CENTER"
echo "=============================================================="

if [[ -f ".venv/bin/python" ]]; then
    PYTHON=".venv/bin/python"
elif command -v python3 >/dev/null 2>&1; then
    PYTHON="python3"
else
    echo "Python 3 is required but not found."
    exit 1
fi

"$PYTHON" server.py
