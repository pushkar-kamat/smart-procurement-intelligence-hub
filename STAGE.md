# Member2 Stage1 Quotations Comparison

**Owner:** Member 2

Adds vendor quotation capture/editing, line calculations and the first comparison view. Price anomaly and vendor risk are intentionally added in later stages.

## Suggested commit
`feat: add quotation capture and comparison workflow`

## Verify before committing
- `Use Swagger to add quotations from invited vendors`
- `Call POST /requisitions/{id}/recalculate and GET /comparison`

## Viva ownership
- Quotation must cover every requisition item exactly once
- Tax/discount/total calculation
- Quotation state locking

