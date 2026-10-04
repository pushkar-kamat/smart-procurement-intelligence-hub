# Deployment guide
Deployment is not performed by this ZIP. Use your own Supabase, Render and Vercel accounts. Service pricing/quotas may vary; no free-tier guarantee is made.

## Supabase
Create project and database, enable email Auth and use RS256/ES256 signing keys. Use the project URL for JWT issuer and JWKS. Root `DATABASE_URL` uses SQLAlchemy `postgresql+psycopg://` format, a URL-encoded password and `sslmode=require`; use direct/session-pooler connection for migrations. Backend connection must own the tables or have appropriate server-only RLS bypass. Do not expose its credentials in frontend. Migration 7bfa01 enables RLS on all app tables without browser policies, preventing PostgREST access. Keep application access through FastAPI.

Create private bucket `procurement-documents`, allow application PDF/PNG/JPEG, set upload cap consistently. No public bucket or browser storage policy is required: API verifies ownership then downloads with its backend service role. Set `STORAGE_BACKEND=supabase`, `SUPABASE_STORAGE_BUCKET`, `SUPABASE_URL` and server-only `SUPABASE_SERVICE_ROLE_KEY`. Local storage on ephemeral Render instances will lose files and is unsuitable without persistent disk.

## Render backend
Connect repository, root directory `backend`, Docker runtime. Dockerfile starts migrations then Uvicorn on `$PORT`. Set DATABASE_URL, SUPABASE_URL, SUPABASE_ANON_KEY, SUPABASE_SERVICE_ROLE_KEY, SUPABASE_JWT_AUDIENCE=authenticated, STORAGE_BACKEND=supabase, bucket and FRONTEND_URL=https://your-vercel-domain. Deploy one instance initially; before scaling, run migrations as a dedicated release step. Health path `/health`. Seed through a trusted local connection or deployment shell (`python -m app.seed`), then optional demo identities. Keep DEMO_PASSWORD out of long-lived hosted env after account creation.

## Vercel frontend
Import same repository with root `frontend`; framework Vite; build `npm run build`; output `dist`; Node 22. Set VITE_API_URL to Render HTTPS base URL without trailing `/api/v1`, VITE_SUPABASE_URL and VITE_SUPABASE_ANON_KEY. `vercel.json` supports React Router deep links. Rebuild to apply VITE changes.

Set Supabase Site URL/redirect allowlist to the actual Vercel origin and update backend CORS FRONTEND_URL. Verify login, /me, every role transition, file upload/download, deep-link refresh, print and full closure. Check RLS denies direct anon/client table reads. Capture actual deployment URLs, commit and date in your evidence pack.

## Known external checks still required
Live Supabase email/login/key rotation, managed Postgres migration, private Storage policies, Render cold-start behavior, Vercel CORS/networking, container execution and hosted CI success. The local test report does not certify these external systems.

Official references: https://supabase.com/docs/guides/auth/jwts ; https://supabase.com/docs/guides/storage/security/access-control .
