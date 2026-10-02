# Member1 Stage1 Requisition Vendors

**Owner:** Member 1

Adds requester requisition lifecycle, vendor master data and vendor invitation/sourcing state transitions.

## Suggested commit
`feat: add requisition vendor and invitation workflow`

## Verify before committing
- `python -m pytest -v`
- `Use Swagger to create, edit, submit and invite a vendor`

## Viva ownership
- DRAFT → SUBMITTED → SOURCING states
- Department/requester authorization
- Vendor active/duplicate invitation guards

