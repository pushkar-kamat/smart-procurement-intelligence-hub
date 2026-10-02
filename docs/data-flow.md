# Data flow and workflow
```mermaid
sequenceDiagram
  participant R as Requester
  participant P as Procurement
  participant A as Approver
  participant F as Finance
  participant API as FastAPI / Database
  R->>API: Draft and submit requisition
  P->>API: Invite vendors and enter complete quotations
  P->>API: Review comparison and explanations
  P->>API: Propose vendor with reason
  A->>API: Approve or reject level 1
  F->>API: Approve level 2 for high-value purchase
  P->>API: Issue approved PO snapshot
  P->>API: Record delivery
  F->>API: Record invoice and reviewed closure
```

```mermaid
stateDiagram-v2
  [*] --> DRAFT
  DRAFT --> SUBMITTED: requester submits
  DRAFT --> CANCELLED: requester cancels
  SUBMITTED --> CANCELLED: requester cancels
  SUBMITTED --> SOURCING: first invitation
  SOURCING --> QUOTATIONS_RECEIVED: complete quotation
  QUOTATIONS_RECEIVED --> COMPARISON_READY: procurement marks ready
  COMPARISON_READY --> QUOTATIONS_RECEIVED: quote edited or added
  COMPARISON_READY --> PENDING_APPROVAL: vendor proposed
  PENDING_APPROVAL --> PENDING_APPROVAL: next approval level
  PENDING_APPROVAL --> REJECTED: rejection
  PENDING_APPROVAL --> APPROVED: all levels approved
  APPROVED --> PO_ISSUED: issue PO
  PO_ISSUED --> PO_ISSUED: partial delivery
  PO_ISSUED --> DELIVERED: full delivery
  DELIVERED --> INVOICED: finance records invoice
  INVOICED --> CLOSED: review and close
```

Terminal rejected/cancelled records remain read-only; create a new request to revise them. There is no arbitrary status-update endpoint. Every business mutation validates the current state. GET comparison is read-only; POST recalculate records readiness and audit. It uses the persisted line analysis calculated at quotation entry/edit, preserving what was evaluated. Taxes apply after a currency-amount discount on each line, rounded half-up to two decimals.
