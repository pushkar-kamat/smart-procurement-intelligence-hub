$ErrorActionPreference = "Stop"
$root = Split-Path $PSScriptRoot -Parent
Start-Process powershell -WorkingDirectory (Join-Path $root "backend") -ArgumentList '-NoExit','-Command','& ../.venv/Scripts/python.exe -m uvicorn app.main:app --reload --port 8000'
Start-Process powershell -WorkingDirectory (Join-Path $root "frontend") -ArgumentList '-NoExit','-Command','npm run dev'
