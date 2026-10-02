# UI prototype and screen map
The executable React interface is the equivalent UI prototype. Visual design uses an institutional green sidebar, high-contrast forms, status badges, responsive tables, progressive workflow tabs and printable PO layout. Typography falls back to system fonts when external fonts cannot load.

| Route / panel | Main content | Primary actor |
|---|---|---|
| /login | Supabase sign-in and requester signup | All |
| / | Visible status counts, estimated value, recent requests | All |
| /requisitions | Search/status filters and request table | All, ownership-filtered |
| /requisitions/new and /:id/edit | Draft header, department and item rows | Requester |
| /requisitions/:id Overview | Item summary, invitation panel, approval record/actions | Role-dependent |
| Quotations tab | Vendor/date/price/tax/discount form, upload/hash | Procurement |
| Comparison tab | Vendor columns, item prices, totals, delivery, expandable explanations | All permitted viewers |
| Audit tab | Actor/time/action/details timeline | All permitted viewers |
| /vendors | Vendor master and factor-level risk table | Procurement edit; others view |
| /approvals | Requests at current user's approval level | Approver/Finance |
| /purchase-orders/:id | Snapshot table/print, delivery, invoice, closure | Role-dependent |
| /operations | Health, metrics, policy, profile access editor | Finance |

Navigation is role-aware but backend gates remain authoritative. Required labels and native validation support keyboard use. Empty/loading/error states are visible; forms disable submit while awaiting response. Under 740px sidebar becomes a horizontal menu; wide matrix scrolls horizontally. Print CSS hides navigation and fulfilment forms.
