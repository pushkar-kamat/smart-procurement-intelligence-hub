# Shared Foundation

Purpose: establish the shared project skeleton before either member adds owned workflow features.

Includes: database schema/migrations, Supabase auth plumbing, common API contracts, shared workflow helpers, seed data, frontend login shell, documentation templates and project configuration.

Suggested commit message:
`chore: establish shared procurement project foundation`

Run after applying:
- `cd backend && python -m pytest -v`
- `cd frontend && npm run build`

This is a shared foundation commit and should not be presented as either member's individual feature work.
