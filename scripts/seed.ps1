$ErrorActionPreference = "Stop"
Set-Location (Join-Path $PSScriptRoot "../backend")
& ../.venv/Scripts/python.exe -m alembic upgrade head
if ($LASTEXITCODE -ne 0) { throw "Migration failed" }
& ../.venv/Scripts/python.exe -m app.seed
if ($LASTEXITCODE -ne 0) { throw "Seed failed" }
