# Smart Procurement Intelligence Hub — technical report
BCA-08 • T.Y. BCA Semester V • two-member project • deadline 3 October 2026

## 1. Problem and scope
Institutional purchasing can involve repeated emails, inconsistent quotations and unclear authorization history. This prototype tests a single digital workflow from requisition to invoice closure. Proposed users are department requesters, procurement officers, purchase committee approvers and finance administrators. Actual stakeholder validation has not yet been collected; it must be added as evidence, not inferred from the brief.

## 2. Requirements and design
The official portfolio requires an integrated procurement prototype, secure APIs, repeatable deployment, automated/failure tests, operational telemetry, baseline comparison and individually demonstrable ownership. The latest user-approved plan removes old tool restrictions and selects React/Vite/Tailwind, FastAPI/Pydantic/SQLAlchemy/Alembic, PostgreSQL and Supabase Auth/Storage. A modular monolith reduces integration overhead while maintaining module boundaries. Architecture, sequence, schema, contracts and UI map are in the design documents.

## 3. Implementation
The server enforces draft editing, submission, sourcing, complete quotations, comparison readiness, selection and amount-based approval. Approval comments and distinct actors are recorded. High-value purchases need committee and finance decisions; roles are checked against DB profiles. Only approved selections generate POs; issued values are stored in snapshots. Delivery precedes invoice. Invoice discrepancies require a documented closure review. Important actions write audit records in the same transaction.

Quotations use Decimal arithmetic, tax on discounted base and half-up rounding. Inputs cannot provide trusted totals. Uploaded PDF/PNG/JPEG documents use random storage keys, metadata and SHA-256. Download checks ownership and recomputes hash before returning bytes. There is no API to overwrite audit logs or issued PO values.

## 4. Intelligence contribution
Price analysis uses historical median and a configurable 25% above-median threshold. At five observations, inclusive quartiles add an IQR boundary. Either boundary can flag a line. Fewer than three matching records yields insufficient history. Exact item and unit matching avoids category-level mixing of unrelated specifications.

Vendor risk combines late delivery (30%), quotation anomalies (25%), disputed orders (20%), incomplete orders (15%) and invoice mismatches (10%). Rates are normalized against relevant counts; missing denominators yield an unscored result. Current records augment synthetic history. Neither intelligence output can independently approve or reject a vendor; human judgement remains mandatory.

## 5. Security and reliability
Supabase JWTs are verified using asymmetric signing keys with issuer/audience/expiry requirements. User-editable metadata cannot assign roles. Requester ownership, endpoint roles and self-approval checks are server-side. PostgreSQL row locks and unique constraints protect transitions and duplicate records. Application tables have RLS enabled with no browser policies. Secrets remain in environment variables. Controlled errors, transaction rollback, health checks, counters and structured request logs support troubleshooting.

## 6. Evaluation
Local automated results and limitations are recorded in build-and-test-report and evidence files. The deterministic three-quotation benchmark checks totals 121540, 127440 and 169920 and measures local TestClient response latency. Unauthorized approval, premature PO, invalid prices, document tampering and storage failure are reproducible experiments.

A meaningful human email/spreadsheet baseline still requires actual timed trials. Local API latency is not a substitute for user cycle time. Live Supabase/PostgreSQL/container deployment, stakeholder acceptance and hosted CI/PR evidence must be captured after configuration. No percentage productivity saving or real-world accuracy is claimed.

## 7. Limitations
This is a synthetic-data industry prototype. It has one currency, one quotation per vendor/request, one PO and invoice, event-level partial delivery, in-memory operational counters and no payment processing. There is no malware scan, global rate limit, automated file orphan cleanup or DB-admin-proof audit ledger. Risk is an explainable policy score rather than a trained predictive model.

## 8. Ownership and evidence
Member 1 owns request/invitation/approval/PO and price analysis vertically. Member 2 owns quotation/comparison/risk/fulfilment/audit vertically. Both share security, integration and evaluation. The generated baseline is a starting implementation, not proof of student authorship or hours. The portfolio's minimum effort, real work logs, reviews, final presentation and demo video must be demonstrated honestly.

## Appendices
Read architecture, data-flow, database-schema, api-contract/OpenAPI, threat-model, test-strategy, acceptance-test-script, baseline-comparison, evaluation-plan, deployment-guide and member-ownership documents. Add actual institution/student/guide details and collected primary evidence before submission.
