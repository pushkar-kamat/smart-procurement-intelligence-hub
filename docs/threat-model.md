# Threat model
Assets: user identity, quotation prices/documents, approval authority, PO snapshots and audit evidence. Trust boundaries: browser/API, API/database, API/auth issuer and API/storage.

| Abuse / failure | Control | Verification |
|---|---|---|
| Forged, expired or wrong-project JWT | PyJWT verifies signature, issuer, audience, required expiry/subject; allowed RS256/ES256 only | signed-token unit integration test |
| Client metadata says finance_admin | metadata ignored, new accounts requester | JWT test |
| Requester approves through direct HTTP | endpoint role guard, self-approval prohibition | 403 and unchanged-state test |
| Two concurrent approvals or POs | PostgreSQL requisition row lock; uniqueness constraints | PostgreSQL CI suite; concurrent-load work remains |
| Alter browser total or skip state | extra fields forbidden; server totals and state machine | validation and premature-PO tests |
| Read another requester's document | requisition ownership before storage access | 403 document test |
| SQL injection | ORM bound parameters; no user SQL construction | code review + strict schemas |
| Direct Supabase table access | PostgreSQL RLS enabled with no anon/authenticated policies | migration SQL; verify on Supabase after deploy |
| Malicious filename or MIME | generated object key; PDF/PNG/JPEG magic signature; byte cap | malformed/oversized/traversal-filename tests |
| Modified stored file | SHA-256 recomputed on download; mismatch returns 409 | integrity tamper test |
| Mutate issued order | no edit endpoint; PO stores snapshot | end-to-end snapshot assertion |
| Modify audit record | no mutation endpoint; DB not exposed to users | API contract + review |
| Database/storage outage | rollback + safe 503; no token/body logs | storage failure test; health DB check |
| Role takeover | only finance updates other users; CLI needed for bootstrap | role guards, own-account change blocked |

## Privacy and retention
Use synthetic/example.com records in demo. Do not upload real sensitive vendor invoices during evaluation. Production retention, backup policy, deletion requests, role separation, antivirus, rate limiting, alerting and formal audit retention are not implemented. Application append-only audit is not tamper-proof against the database owner. Admin/operator access must be tightly controlled.

CORS permits only configured frontend origins. HTTPS is required for deployment. Bearer auth is not cookie-based, so server CSRF tokens are not used. Tokens reside in the Supabase browser session; XSS defenses and dependency maintenance remain important. Files download as attachments with nosniff; magic-signature validation is not a malware scanner.

Reference: https://supabase.com/docs/guides/auth/jwts and https://supabase.com/docs/guides/storage/security/access-control (consulted for issuer/JWKS and server-only storage access).
