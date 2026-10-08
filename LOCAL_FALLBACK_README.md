# Smart Procurement — Local Docker/Auth Fallback V6

This patch makes Docker and Supabase optional for local development/demo use while preserving the existing Docker + Supabase path.

## Supported modes

### 1. Existing Docker + Supabase mode
Nothing is removed. Continue using your current workflow:

```cmd
docker compose up -d
```

and keep:

```env
AUTH_PROVIDER=supabase
VITE_AUTH_PROVIDER=supabase
```

### 2. Zero-cloud / zero-Docker fallback

Run:

```cmd
RUN_LOCAL.cmd
```

This starts:

- FastAPI directly with Python
- Vite directly with npm
- local SQLite database at `backend/procurement-local.db`
- local JWT authentication
- PBKDF2-SHA256 password hashes
- local document storage

Docker and Supabase are not required in this mode.

### 3. Direct local PostgreSQL + local auth

If PostgreSQL is installed directly on Windows:

```cmd
set LOCAL_DATABASE_URL=postgresql+psycopg://procurement:YOUR_PASSWORD@127.0.0.1:5432/procurement
RUN_LOCAL_POSTGRES.cmd
```

This gives the same direct Python/Vite experience but keeps PostgreSQL.

## Authentication providers

Backend:

```env
AUTH_PROVIDER=supabase
```

or:

```env
AUTH_PROVIDER=local
```

The backend also accepts `auto` for migration/testing, but the recommended normal configurations are explicit `supabase` or `local`.

Frontend:

```env
VITE_AUTH_PROVIDER=supabase
```

or:

```env
VITE_AUTH_PROVIDER=local
```

## Local demo accounts

The bootstrap enables local credentials for the seeded staff and active vendors.

Password:

`Procure123`

Examples:

- requester@procure.com
- procurement@procure.com
- approver@procure.com
- finance@procure.com
- vendor.vertex@procure.com
- vendor.northstar@procure.com
- vendor.bluebell@procure.com

Approved suppliers created through the vendor-application workflow can also create their own local vendor account from the Vendor Portal.

## Security

Local passwords are never stored in plain text.

They are stored using:

`PBKDF2-HMAC-SHA256 + random 16-byte salt + 310,000 iterations`

The browser receives a time-limited HS256 local JWT. The local signing secret is server-side only.

The hard-coded secret inside `RUN_LOCAL.cmd` is only for an offline classroom/development fallback. Do not use it for a public deployment.

## Password reset in local mode

Offline local mode cannot send a password-reset email.

For the seeded demo users use:

`Procure123`

or rerun:

```cmd
cd backend
..\.venv\Scripts\python.exe -m app.seed_local_users
```

Supabase mode keeps the normal email reset workflow.

## Database note

`RUN_LOCAL.cmd` deliberately uses a separate SQLite fallback database. It does not copy the Docker PostgreSQL volume.

If you need direct/local mode with PostgreSQL, use `RUN_LOCAL_POSTGRES.cmd` and point `LOCAL_DATABASE_URL` at a local PostgreSQL database.

## Deployment

For your normal hosted deployment, continue using:

- Vercel for frontend
- Render/Docker-capable backend hosting
- managed PostgreSQL
- Supabase Auth

Docker is not inherently mandatory in production, but keeping the containerized deployment is useful for reproducibility.

Local authentication is primarily a fallback/offline mode. Cognito can be added later as another hosted provider, but it is not needed for this capstone.

## Apply

Extract into:

`C:\smart-procurement-staged`

Run:

`APPLY_LOCAL_FALLBACK_V6.cmd`

Then apply the one new migration in your normal database:

```cmd
cd backend
..\.venv\Scripts\python.exe -m alembic upgrade head
..\.venv\Scripts\python.exe -m pytest -q
```

For offline/local mode after that:

```cmd
cd ..
RUN_LOCAL.cmd
```

## Rollback

Modified files receive `.before-local-fallback-v6` backups.

The new migration is `h6d3e4_local_auth.py`.
