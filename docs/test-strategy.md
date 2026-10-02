# Test strategy
Backend tests run through real FastAPI routes and SQLAlchemy against an isolated database. Default fixtures create a fresh SQLite in-memory DB per test and enable foreign keys. `TEST_DATABASE_URL` selects PostgreSQL and a new random schema per test; the schema is removed afterwards. Never point the migration smoke helper at a valuable database.

Workflow tests override the identity dependency only inside pytest; no test-auth route or role-switch flag ships in the runtime. A separate signed JWT test uses real RSA signatures and verifies signature/issuer/audience/expiry, with an injected JWKS key provider. Live Supabase login and key rotation require external verification.

Critical suite: deterministic monetary totals; median/IQR policy and insufficient history; weighted risk; full two-level approval lifecycle; duplicate decisions/invitations; missing/invalid token; requester/finance restrictions; ownership; malformed values; state skipping; preapproval PO; tampered/oversized/malformed files; controlled storage failure; draft/cancel; rejection; single-level approval.

Frontend: Vitest + Testing Library verify protected-route redirect, authenticated content, role visibility, requisition validation and risk/anomaly matrix output. Build verifies JSX/bundle integration. See evidence files for actual results, not target claims. Manual acceptance covers real browser forms/auth and printing. CI defines PostgreSQL, container builds and audits, but a successful hosted run still needs to be captured.
