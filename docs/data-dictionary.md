# Data dictionary and calculation conventions
See `database-schema.md` for every column/type/reference and `openapi.json` for input validation.

| Concept | Definition |
|---|---|
| estimated_total | Sum of quantity × estimated unit price, each line rounded to 2 decimals |
| quotation subtotal | Sum of rounded unit price × requisition quantity; client cannot submit quantity or grand total |
| discount | Currency amount per line, not percent; must be strictly below line subtotal |
| tax | Calculated currency amount; input tax_percent applies to discounted line subtotal |
| grand_total | Subtotal − discount_total + tax_total; all INR |
| quantity | Positive decimal, <=10000, up to 3 decimal places |
| money input | Positive <=10000000, up to 2 decimals; aggregate Numeric(16,2) |
| analysis.reference_median | Median of exact item+unit historical observations up to quote date |
| analysis.deviation_percent | (unit price − median)/median × 100 |
| analysis.threshold_percent | Configured default 25; strict greater-than comparison |
| analysis.q1/q3/iqr | Inclusive quartiles, Q3−Q1; populated for >=5 observations |
| analysis.upper_boundary | Q3 + 1.5×IQR |
| analysis.anomaly_flag | Above percentage threshold OR upper statistical boundary |
| INSUFFICIENT_HISTORY | <3 matching price observations, or insufficient vendor factor denominators |
| risk.score | Sum of rate × weight, 0–100; None when history cannot support all factors |
| risk.band | Low <=29.99; Medium <=59.99; otherwise High (configured cutoffs) |
| late-delivery rate | Late / completed deliveries; weight 30 |
| quotation-anomaly rate | Flagged lines / quotation lines; weight 25 |
| disputed-order rate | Disputed/rejected historical orders / total orders; weight 20 |
| incomplete-order rate | Incomplete orders / total orders; weight 15; current unfulfilled orders only after due date |
| invoice-mismatch rate | Mismatched invoices / invoiced orders; weight 10 |
| approval_plan | Matching DB rules snapshotted at vendor proposal; sequential distinct-person approval |
| snapshot_json | Approved requisition, items, quotation and vendor fields copied at PO issuance |
| document.sha256 | Hex SHA-256 over received raw bytes; recomputed before download |
| mismatch_flag | Absolute invoice−PO deviation / PO ×100 exceeds configured default 5% |
| audit.details | Safe JSON action context, excluding credentials and file bytes |

All IDs are integers except Supabase subject and generated storage keys. Server timestamps are UTC; dates are calendar dates. Profiles contain a verified external identity and internal role. Strings have input limits and are rendered by React as escaped text. No client-supplied SQL identifiers are accepted.
