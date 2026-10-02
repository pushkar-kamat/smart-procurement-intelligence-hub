$ErrorActionPreference = "Stop"
Set-Location (Join-Path $PSScriptRoot "..")
if (!(Test-Path .env)) { Copy-Item .env.example .env }
if (!(Test-Path frontend/.env)) { Copy-Item frontend/.env.example frontend/.env }
py -3.12 -m venv .venv
& ./.venv/Scripts/python.exe -m pip install -r backend/requirements-dev.txt
if ($LASTEXITCODE -ne 0) { throw "Backend dependency install failed" }
Push-Location frontend
npm ci
if ($LASTEXITCODE -ne 0) { throw "Frontend dependency install failed" }
Pop-Location
Write-Host "Configure both .env files and Supabase before continuing. See README.md."
