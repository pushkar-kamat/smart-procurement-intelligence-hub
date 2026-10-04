# Presentation content — adapt into your college slide template
1. **Title and team:** BCA-08, full project title, member names and guide (enter actual names).
2. **Purchasing problem:** requisitions, supplier offers and approval history scattered across email/spreadsheets. Distinguish assumed pain points from collected stakeholder evidence.
3. **Users and scope:** requester, procurement, approver, finance; request-to-close workflow; no payments/IoT/LLM.
4. **Architecture:** React → FastAPI → PostgreSQL; Supabase identity/private files; one modular backend.
5. **Workflow demonstration:** draft → sourcing → quotes → comparison → approval → PO → delivery → invoice → closed.
6. **Price intelligence:** median 52000; quote 72000; +38.46%; percentage/IQR explanation; insufficient-data case.
7. **Vendor intelligence:** five factors and weights; transparent rates; Low/Medium/High/unknown; human selection.
8. **Security and integrity:** verified JWT, DB roles, ownership, state guard, PO snapshot, document SHA-256, audit.
9. **Evaluation:** use actual test report and benchmark; add measured manual comparison and deployed evidence after execution.
10. **Robustness:** requester approval attempt returns 403 with unchanged state; PO before approval blocked; tampered file blocked.
11. **Ownership:** each member's full-stack modules, real changes/PR review and actual hours.
12. **Limits and next steps:** synthetic data, single currency, production hardening; never claim pending deployment/video evidence as done.
