# Quick start — Smart Procurement Intelligence Hub

BCA-08 · React + FastAPI + PostgreSQL · two-member capstone prototype.

## 1. Prepare your machine
Install Python **3.12**, Node.js **22 LTS**, Git and Docker Desktop (for PostgreSQL). Open the extracted project folder in VS Code. Keep your older Java project separate; this is a new FastAPI project.

In PowerShell, from this folder:
```powershell
./scripts/setup.ps1
```
If your machine blocks PowerShell scripts, run these commands directly; do not change organization security policies:
```powershell
py -3.12 -m venv .venv
./.venv/Scripts/python.exe -m pip install --upgrade pip
./.venv/Scripts/python.exe -m pip install -r backend/requirements-dev.txt
Copy-Item .env.example .env
Copy-Item frontend/.env.example frontend/.env
cd frontend
npm ci
cd ..
```
Copies are needed only if your `.env` files do not already exist. Linux/macOS: `bash scripts/setup.sh` (Python 3.12 required).

## 2. Configure Supabase and PostgreSQL
Create your own Supabase project. In Auth, enable email/password and use an asymmetric **RS256 or ES256** signing key. This backend intentionally does not accept legacy HS256 tokens. Set the Site URL and allowed redirect URL to `http://localhost:5173` for local signup confirmation. Hosted projects need their actual HTTPS frontend URL.

Edit root `.env`:
- `POSTGRES_PASSWORD`: choose a local development password. For the Compose URL, use letters/numbers to avoid URL-encoding ambiguity. It is never committed.
- `DATABASE_URL`: set `postgresql+psycopg://procurement:YOUR_PASSWORD@localhost:5432/procurement` for native backend + Docker DB.
- `SUPABASE_URL`: your project URL.
- `SUPABASE_ANON_KEY`: your publishable/anon client key, not a service-role key.
- `SUPABASE_SERVICE_ROLE_KEY`: only needed for optional user seeding and Supabase file storage. Backend only.
- `DEMO_PASSWORD`: demo password used when creating/migrating seeded accounts. For the classroom demo use `Procure123`.

Edit `frontend/.env` with `VITE_API_URL=http://localhost:8000`, `VITE_SUPABASE_URL` and `VITE_SUPABASE_ANON_KEY` using the same project. **Never put a service-role key or DB password in a VITE variable.**

Supabase authentication is required for the application. There is no unauthenticated demo login or runtime role switch. Automated tests use isolated fixtures.

## 3. Start the database, migrate and seed
```powershell
docker compose up -d db
./scripts/seed.ps1
```
Or from `backend`:
```powershell
../.venv/Scripts/python.exe -m alembic upgrade head
../.venv/Scripts/python.exe -m app.seed
```
The seed creates 3 departments, 10 vendors, 10 item types, 80 historical prices, 3 requisitions and 2 approval levels. All records are synthetic. Repeated seeding leaves existing data intact.

You can instead connect `DATABASE_URL` directly to your Supabase PostgreSQL database. Use the dashboard connection string, change its scheme to `postgresql+psycopg://`, URL-encode the password and append `?sslmode=require`. Prefer a direct connection or session pooler for migrations. Use a database owner account for these prototype migrations; browser clients are blocked by RLS and must use FastAPI. See `docs/deployment-guide.md`.

## 4. Create your demo identities
With root `.env` values `SUPABASE_SERVICE_ROLE_KEY` and `DEMO_PASSWORD` configured:
```powershell
cd backend
../.venv/Scripts/python.exe -m app.seed_users
cd ..
```
Creates/links these role templates, without printing or storing passwords:

Demo password: `Procure123` (local/classroom demo only).

| Email | Role |
|---|---|
| requester@procure.com | requester |
| procurement@procure.com | procurement |
| approver@procure.com | approver |
| finance@procure.com | finance_admin |

Existing Supabase users keep their passwords. The utility links the synthetic requester's records to the real demo identity. Use only in your own demo project. No invitations or emails are sent by the utility.

Alternative: create real accounts through signup and confirm email. Their first sign-in creates a requester profile. Bootstrap one administrator through the operator CLI, after that first sign-in:
```powershell
cd backend
../.venv/Scripts/python.exe -m app.manage_profile your-email@procure.com finance_admin
```
That administrator can assign other signed-in profiles from Operations. Operator role changes are audited. Normal signup can never choose a privileged role.

## 5. Start both apps
From the project root:
```powershell
./scripts/run-dev.ps1
```
Or use two terminals:
```powershell
# Terminal 1, from backend/
../.venv/Scripts/python.exe -m uvicorn app.main:app --reload --port 8000
# Terminal 2, from frontend/
npm run dev
```
Open `http://localhost:5173`. Swagger: `http://localhost:8000/docs`. Health: `http://localhost:8000/health`.

**Docker alternative:** after filling root `.env`, run `docker compose up --build -d`, then `docker compose exec backend python -m app.seed` and optionally `docker compose exec backend python -m app.seed_users`. Open `http://localhost:8080`. Compose runs migrations automatically; native setup uses explicit Alembic commands. Frontend configuration is baked at build time, so rebuild after changing keys.

## What the system does
Requester drafts/submits a requisition. Procurement invites vendors, records quotations and optional PDF/images, compares prices/risk, and proposes a vendor. An approver decides; totals of at least INR 100,000 require a second finance approval. Procurement issues an immutable PO snapshot. Procurement/finance records delivery; finance records invoice and closes after documenting review. Server-side audit records every important action.

Price checks use the median, an above-median percentage rule and IQR boundaries. Vendor risk uses five weighted factors. These are transparent rules, not a trained ML model. A human always selects and approves vendors.

## Test and verify
```powershell
cd backend
../.venv/Scripts/python.exe -m pytest -q
../.venv/Scripts/python.exe -m alembic check
../.venv/Scripts/python.exe ../scripts/run_baseline_benchmark.py
../.venv/Scripts/python.exe -m pip_audit -r requirements.txt
cd ../frontend
npm test
npm run build
npm audit
```
For the PostgreSQL API suite, from `backend/` set `$env:TEST_DATABASE_URL` to a **disposable PostgreSQL database** and run pytest. Each test creates and drops a unique schema. Unset this variable afterwards. SQLite is only a lightweight test fallback, not the recommended multi-user database.

Build containers: `docker compose config --quiet`, `docker compose build`. GitHub Actions supplies PostgreSQL and runs migrations, the API suite, UI tests, build and dependency scans after you push the repository. Included CI YAML is not proof that a hosted CI run has happened.

## Project map
- `backend/app/routers/procurement.py`: REST routes, role checks and transaction orchestration.
- `backend/app/services/`: workflow helpers, statistics, risk, money and storage.
- `backend/app/models/`: relational model; `alembic/versions`: versioned migrations.
- `frontend/src/`: functional pages, reusable UI, Supabase auth and API client.
- `data/seed/`: reference prices, vendor history and benchmark quotations.
- `docs/`: requirements, architecture, security, evaluation, guides and actual build evidence.
- `scripts/`: setup, benchmark and PostgreSQL validation helpers.

## Deployment and remaining external work
See `docs/deployment-guide.md` for Vercel frontend, Render API and Supabase database/auth/storage. Use Supabase storage on ephemeral hosting; local uploads require a persistent disk. You must supply your own service credentials and accounts. No deployment was performed as part of ZIP generation.

See `docs/build-and-test-report.md` for exactly what ran here. Docker/PostgreSQL runtime and live Supabase integration must be checked in your environment. You must also record the actual manual baseline timings, stakeholder feedback, peer reviews, individual work hours and 5–8 minute demo video. No academic evidence has been invented.
