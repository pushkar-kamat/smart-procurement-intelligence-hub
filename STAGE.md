# Final Integration

Merge both members' completed work and normalize to the tested working snapshot. This stage owns cross-cutting integration only: Supabase token validation, configuration, CORS, Docker, CI, deployment files, full end-to-end regression suite and final evidence/documentation.

Suggested commit message:
`chore: integrate final tested procurement application`

Final verification:
1. `cd backend && python -m pytest -v`
2. `python -m pip_audit`
3. `cd frontend && npm test && npm run build && npm audit`
4. `docker compose up -d --build`
5. `docker compose ps`
6. Test login and one complete procurement workflow.

Do not backdate commits. Treat the staged history as current integration/ownership evidence from an existing prototype.
