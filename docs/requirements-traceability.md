# Requirements traceability
Priority: master prompt → latest workflow → official portfolio BCA-08 and baseline. Stack suggestions overridden; behavioral requirements retained.

| Requirement | Implementation | Verification / remaining evidence |
|---|---|---|
| Identity and server roles | core/auth.py; profiles; Supabase JS | JWT/RBAC tests; live Supabase pending |
| Requisition / invitations | routers/procurement.py; DRAFT/SUBMITTED/SOURCING | draft/state/duplicate tests; browser acceptance |
| Quote upload / arithmetic | schemas; calculate_line; storage | totals, invalid fields, file/hash tests |
| Comparison + human selection | ComparisonMatrix; comparison/selection routes | UI test + lifecycle test |
| Explainable price anomaly | analyze_price; persisted analysis JSON | median/IQR/insufficient history tests |
| Explainable vendor risk | vendor_risk + risk_for | low/medium/high/unknown tests |
| Approval levels | approval_rules; frozen approval_plan | two-level/single/reject/duplicate/self tests |
| PO / delivery / invoice | snapshot_json; fulfilment routes | lifecycle, preapproval guard, mismatch |
| Audit and operations | audit_logs; middleware; /health, /metrics | expected actions, error counters, health tests |
| Contracts and architecture | OpenAPI; schema/data-flow/docs | generated API/schema references |
| Security/failure experiment | robust pytest cases + manual procedure | actual local fixture results; deployed run pending |
| Repeatable deployment | Alembic, Dockerfiles, Compose, CI | SQLite migration checks; real Docker/PG pending |
| Baseline / measurable evaluation | benchmark script + timing worksheet | deterministic results; manual timings pending |
| Data package | seed.py; CSVs; provenance/dictionary | 80 price observations, synthetic labels |
| Two-member ownership | member-ownership + work logs/backlog | real student work/reviews to collect |
| Academic final evidence | final-report.md; presentation-outline.md; demo script | actual stakeholder/video/PR/hosted evidence pending |
