#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

echo "=============================================================="
echo "Installing WJC GLOBAL GROUP — JARVIS COMMAND CENTER"
echo "=============================================================="

if ! command -v python3 >/dev/null 2>&1; then
  printf 'Python 3 is required but was not found.\n' >&2
  exit 1
fi

if [ ! -d ".venv" ]; then
  printf 'Creating Python virtual environment...\n'
  python3 -m venv .venv
fi

printf 'Installing dependencies from requirements.txt...\n'
.venv/bin/pip install -r requirements.txt

if [ ! -f .env ]; then
  cp .env.example .env
  printf 'Created private .env from .env.example.\n'
fi

chmod +x start.sh install.sh

printf '\nJARVIS Command Center installed successfully.\n'
printf 'Run ./start.sh to launch.\n'
