#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
(cd backend && ../.venv/bin/python -m uvicorn app.main:app --reload --port 8000) &
backend_pid=$!
trap 'kill "$backend_pid" 2>/dev/null || true' EXIT
(cd frontend && npm run dev)
