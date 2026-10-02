#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
[ -f .env ] || cp .env.example .env
[ -f frontend/.env ] || cp frontend/.env.example frontend/.env
python3.12 -m venv .venv
.venv/bin/python -m pip install -r backend/requirements-dev.txt
(cd frontend && npm ci)
echo 'Configure both .env files and Supabase; read README.md.'
