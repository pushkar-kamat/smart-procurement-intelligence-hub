# Project overview
**BCA-08: Smart Procurement Intelligence Hub with Vendor Risk and Price-Anomaly Detection.** T.Y. BCA Semester V; two members; deadline 3 October 2026.

Small institutional purchases pass through email, spreadsheets and manual approval tracking. This prototype centralizes requisitions, vendor invitations, quotation calculations, comparisons, approval levels, purchase orders, delivery, invoice and audit history. It is intended for stakeholder testing with synthetic data, not production financial settlement.

## Stakeholders and user stories
| Stakeholder | Need | Implemented outcome |
|---|---|---|
| Department requester | Describe and track purchases | Owned drafts, line items, submission, status/audit |
| Procurement officer | Compare equivalent offers | Invitations, complete quotations, matrix, risk/price evidence, selection |
| Purchase committee | Authorize valid purchases | Amount-based approval plan, comments, actor/time |
| Finance administrator | Reconcile delivery and invoices | Second-level approval, mismatch review, closure, access admin |
| Vendor | Provide accurate offer documents | Procurement records offers on vendor's behalf |

## Scope
Single institution, one currency (INR), one quotation per vendor per request, one issued PO and invoice per requisition, full-order final delivery with optional partial-delivery events. No payments, vendor self-service, real invitation emails, inventory accounting, ML training or automatic decisions.

Stakeholder interviews/current-process observations are **not yet collected**. Validate these proposed personas and pain points with the college purchase department; use the evaluation worksheets. Do not claim the synthetic scenario is institutional procurement evidence.

## Source decisions
The attached master prompt takes priority, followed by Latest Workflow Plan and the official portfolio (programme baseline pp. 2–4; BCA-08 pp. 25–26). The confirmed technology freedom replaces older Java/Spring/IoT suggestions with React/FastAPI/PostgreSQL. End-to-end behavior and engineering/evaluation evidence are preserved. The portfolio requires 100 documented hours per student; record genuine work only and discuss feasibility with the guide.
