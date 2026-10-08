@echo off
setlocal
cd /d "%~dp0"

if "%LOCAL_DATABASE_URL%"=="" (
  echo LOCAL_DATABASE_URL is not set.
  echo.
  echo Example:
  echo set LOCAL_DATABASE_URL=postgresql+psycopg://procurement:YOUR_PASSWORD@127.0.0.1:5432/procurement
  echo RUN_LOCAL_POSTGRES.cmd
  echo.
  pause
  exit /b 1
)

if not exist ".venv\Scripts\python.exe" (
  echo Python virtual environment was not found.
  pause
  exit /b 1
)

set AUTH_PROVIDER=local
set LOCAL_AUTH_SECRET=smart-procurement-local-dev-only-change-for-production-2026
set LOCAL_AUTH_TOKEN_MINUTES=480
set DATABASE_URL=%LOCAL_DATABASE_URL%
set FRONTEND_URL=http://localhost:5173
set STORAGE_BACKEND=local
set LOCAL_UPLOAD_DIR=./uploads
set DEMO_PASSWORD=Procure123

pushd backend
"..\.venv\Scripts\python.exe" -m alembic upgrade head
if errorlevel 1 goto :failed
"..\.venv\Scripts\python.exe" -m app.seed
if errorlevel 1 goto :failed
"..\.venv\Scripts\python.exe" -m app.seed_vendor_marketplace
if errorlevel 1 goto :failed
"..\.venv\Scripts\python.exe" -m app.seed_local_users
if errorlevel 1 goto :failed
popd

start "Smart Procurement API - LOCAL POSTGRES" cmd /k "cd /d ""%CD%\backend"" && set AUTH_PROVIDER=local&& set LOCAL_AUTH_SECRET=smart-procurement-local-dev-only-change-for-production-2026&& set LOCAL_AUTH_TOKEN_MINUTES=480&& set DATABASE_URL=%LOCAL_DATABASE_URL%&& set FRONTEND_URL=http://localhost:5173&& ..\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --port 8000"

start "Smart Procurement UI - LOCAL POSTGRES" cmd /k "cd /d ""%CD%\frontend"" && set VITE_AUTH_PROVIDER=local&& set VITE_API_URL=http://localhost:8000&& npm run dev"

echo Local PostgreSQL mode started.
exit /b 0

:failed
popd
echo Local PostgreSQL bootstrap failed.
pause
exit /b 1
