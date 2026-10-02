# Actual build and test report
Execution date: 29 September 2026. Linux x86_64; Python 3.12.14. A local isolated Python venv and npm dependency installation were used. This report records local execution, not a hosted CI or deployment certification.

| Check / actual command | Actual result | Evidence / scope |
|---|---|---|
| `python -m venv .venv`, pip dependency installation | Passed | Runtime/dev dependencies installed |
| `python -m pytest -q` from backend | 19 passed | evidence/pytest.txt; isolated SQLite with FK checks |
| `alembic revision --autogenerate` | Initial migration generated | versioned schema file included |
| `alembic upgrade head`, `alembic check` | Passed; no pending schema operations | evidence/migrations.txt |
| `alembic downgrade base` then `alembic upgrade head` | Passed on disposable local SQLite DB | migration round-trip |
| `python -m app.seed` twice | First creates data; second no-op | evidence/migrations.txt |
| PostgreSQL URL + `alembic upgrade head --sql` | SQL generation passed | evidence/postgres-migration.sql; **not executed on PostgreSQL** |
| `python scripts/run_baseline_benchmark.py` | 3/3 totals match; 100 API iterations | evidence/baseline-benchmark.json |
| Uvicorn subprocess + HTTP GET health/docs/OpenAPI | All 200 | evidence/http-smoke.json and server-smoke-log.txt |
| `npm install`, then `npm test` | 6 passed | evidence/frontend-tests.txt |
| `npm run build` | Passed | evidence/frontend-build.txt |
| `npm audit --json` after dev dependency fix | 0 findings | evidence/npm-audit.json |
| `pip-audit --format json` after upgrading pip | No known vulnerabilities | evidence/pip-audit.json; installed isolated environment |

## Measured benchmark
The identical 3-vendor seeded matrix returns totals 121540, 127440 and 169920. On 100 local TestClient requests, median 7.417 ms, p95 9.857 ms and maximum 60.706 ms. These are one local measurement, not a deployed SLA, load/concurrency result or human cycle-time saving. Manual baseline and application user task times are null/unmeasured in the output.

## Issues fixed during validation
- Pytest import path needed explicit project configuration; `pyproject.toml` now sets it.
- Initial development dependency scan found moderate Vitest/mocker advisories; Vitest was updated to 4.1.11, tests/build rerun and final npm audit is clean.
- The execution environment's old pip version had advisories; upgraded to 26.2.1 and rescanned. Application dependency findings were not observed in the final scan. Users should upgrade local pip before installation and repeat scans over time.
- SQLAlchemy transaction dependencies complete at function scope so DB commit errors occur before returning successful responses.
- Supabase Data API bypass is addressed by a separate PostgreSQL RLS migration with no browser policies.

## Checks unavailable or not claimed
- Docker binary was not available; `docker compose config` and image builds **not run**. YAML was parsed for structural validation only. CI and user commands include real Docker gates.
- No PostgreSQL server/client was installed. A normal package installation attempt failed on OS setgroups/setuid permissions. No permissions were bypassed. PostgreSQL runtime, row locks and RLS remain unverified here; dedicated isolated-schema tests and CI service are included.
- No Supabase project credentials were supplied. Real login/signup/email confirmation, live JWKS rotation, managed storage and managed database connectivity **not run**. Cryptographic JWT tests used real RSA signatures with test keys, and workflow tests used pytest-only identity fixtures.
- No browser binary was installed. Playwright's Chromium download returned invalid/truncated archives. Browser screenshots and visual/manual end-to-end UI verification **not completed**; none are fabricated. Vitest DOM tests and Vite production build passed.
- No Render/Vercel deployment, actual GitHub CI run, PR review, stakeholder interview, timed human baseline or demo video was performed.

## Warnings
FastAPI/Starlette emitted a deprecation notice for the current httpx TestClient adapter. The specified FastAPI TestClient/httpx tests passed; migrating that adapter is future dependency maintenance. npm's host-level proxy-config warning did not affect tests or build. No real secrets are included in the ZIP.
