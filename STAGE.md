# Member1 Stage3 Purchase Order

**Owner:** Member 1

Adds purchase-order generation after final approval and immutable quotation/requisition snapshots.

## Suggested commit
`feat: add purchase order generation and snapshot`

## Verify before committing
- `Approve a requisition then POST /purchase-order`
- `GET the generated purchase order`

## Viva ownership
- PO allowed only after APPROVED
- Vendor/quotation validity re-check
- Immutable snapshot used for issued values

