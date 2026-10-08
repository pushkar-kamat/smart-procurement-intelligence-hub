@echo off
setlocal
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
  echo Python virtual environment was not found.
  echo Run scripts\setup.ps1 first, or create .venv with Python 3.12.
  pause
  exit /b 1
)

if not exist "frontend\node_modules" (
  echo frontend\node_modules is missing.
  echo Run: cd frontend ^&^& npm ci
  pause
  exit /b 1
)

set AUTH_PROVIDER=local
set LOCAL_AUTH_SECRET=smart-procurement-local-dev-only-change-for-production-2026
set LOCAL_AUTH_TOKEN_MINUTES=480
set DATABASE_URL=sqlite:///./procurement-local.db
set FRONTEND_URL=http://localhost:5173
set STORAGE_BACKEND=local
set LOCAL_UPLOAD_DIR=./uploads
set DEMO_PASSWORD=Procure123

echo.
echo ============================================================
echo  SMART PROCUREMENT - DIRECT LOCAL FALLBACK
echo ============================================================
echo  Docker:        NOT REQUIRED
echo  Supabase Auth: NOT REQUIRED
echo  Database:      backend\procurement-local.db ^(SQLite fallback^)
echo  Auth:          Local JWT + PBKDF2 password hashes
echo ============================================================
echo.

pushd backend
"..\.venv\Scripts\python.exe" -m app.local_bootstrap
if errorlevel 1 goto :failed
popd

start "Smart Procurement API - LOCAL" cmd /k "cd /d ""%CD%\backend"" && set AUTH_PROVIDER=local&& set LOCAL_AUTH_SECRET=smart-procurement-local-dev-only-change-for-production-2026&& set LOCAL_AUTH_TOKEN_MINUTES=480&& set DATABASE_URL=sqlite:///./procurement-local.db&& set FRONTEND_URL=http://localhost:5173&& set STORAGE_BACKEND=local&& set LOCAL_UPLOAD_DIR=./uploads&& ..\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --port 8000"

start "Smart Procurement UI - LOCAL" cmd /k "cd /d ""%CD%\frontend"" && set VITE_AUTH_PROVIDER=local&& set VITE_API_URL=http://localhost:8000&& npm run dev"

echo.
echo Local fallback started.
echo Frontend: http://localhost:5173
echo Backend:  http://localhost:8000
echo Swagger:  http://localhost:8000/docs
echo.
echo Demo accounts use password: Procure123
echo.
exit /b 0

:failed
popd
echo.
echo Local bootstrap failed. Review the error above.
pause
exit /b 1
