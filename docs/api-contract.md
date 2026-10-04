# API contract

Complete machine-readable request/response contract: `openapi.json` (also `/openapi.json` and `/docs` at runtime). All `/api/v1` endpoints require bearer authentication; `/health` is public and `/metrics` finance-only.

Requests use strict Pydantic models (unknown fields rejected). Money is validated as Decimal and totals recalculated. Errors return `detail`; validation errors include structured field paths. 401 missing/invalid identity; 403 role/ownership; 404 missing entity; 409 state/duplicate; 413 upload size; 422 input; 503 service unavailable.

| Method | Path | Operation |
|---|---|---|
| GET | `/health` | Health |
| GET | `/metrics` | Metrics |
| GET | `/api/v1/me` | Me |
| GET | `/api/v1/departments` | Departments |
| GET | `/api/v1/profiles` | Profiles |
| PATCH | `/api/v1/profiles/{id}` | Update Profile |
| GET | `/api/v1/approval-rules` | Approval Rules |
| GET | `/api/v1/requisitions` | Requisitions |
| POST | `/api/v1/requisitions` | Create Requisition |
| GET | `/api/v1/requisitions/{id}` | Get Requisition |
| PUT | `/api/v1/requisitions/{id}` | Edit Requisition |
| POST | `/api/v1/requisitions/{id}/submit` | Submit |
| POST | `/api/v1/requisitions/{id}/cancel` | Cancel |
| GET | `/api/v1/vendors` | Vendors |
| POST | `/api/v1/vendors` | Create Vendor |
| PUT | `/api/v1/vendors/{id}` | Update Vendor |
| GET | `/api/v1/vendors/{id}/risk` | Risk |
| GET | `/api/v1/requisitions/{id}/invitations` | Invitations |
| POST | `/api/v1/requisitions/{id}/invitations` | Invite |
| POST | `/api/v1/requisitions/{id}/quotations` | Quotation |
| GET | `/api/v1/requisitions/{id}/quotations` | Quotes |
| PUT | `/api/v1/quotations/{id}` | Edit Quote |
| GET | `/api/v1/quotations/{id}` | Quote Detail |
| POST | `/api/v1/requisitions/{id}/recalculate` | Recalculate |
| GET | `/api/v1/requisitions/{id}/comparison` | Comparison |
| POST | `/api/v1/requisitions/{id}/send-for-approval` | Send For Approval |
| GET | `/api/v1/approvals/inbox` | Inbox |
| POST | `/api/v1/requisitions/{id}/approval` | Approve |
| POST | `/api/v1/requisitions/{id}/purchase-order` | Issue Po |
| GET | `/api/v1/purchase-orders/{id}` | Po Detail |
| POST | `/api/v1/purchase-orders/{id}/delivery` | Delivery |
| POST | `/api/v1/purchase-orders/{id}/invoice` | Invoice |
| POST | `/api/v1/purchase-orders/{id}/close` | Close |
| POST | `/api/v1/quotations/{id}/file` | Quote File |
| POST | `/api/v1/invoices/{id}/file` | Invoice File |
| GET | `/api/v1/documents/{id}` | Download |
| GET | `/api/v1/requisitions/{id}/audit` | Logs |