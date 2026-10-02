# End-to-end acceptance script
Use a dedicated synthetic environment and four separate browser profiles or sign out between roles. Record date, tester, commit and environment before starting.

1. Requester signs in. Create a new IT requisition with Business laptop, category Computers, unit piece, quantity 2, estimated unit price 52000. Justification: replace two ageing lab machines. Expected estimated total 104000. Save draft, edit description, submit.
2. Procurement signs in. Open request and invite Cedar, Northstar and Harbor (first 3 vendors). Duplicate invite must fail without duplicate rows.
3. Enter three quotes for exactly the same specification: unit prices 51500, 54000 and 72000; quantity comes from request, tax 18%, discount 0, delivery 10/13/16 days. Attach a valid PDF to a quote.
4. Open Comparison. Totals must be 121540, 127440, 169920. Harbor's unit price must flag against median 52000; explanation +38.46%. Inspect risk factors for all vendors. Low price must not auto-select a winner.
5. Mark comparison ready. Choose Cedar and enter a rationale. Send for approval. Quotes can no longer be edited. Approval plan must show committee then finance (total >= 100000).
6. Requester attempts direct approval: expect 403 and unchanged PENDING_APPROVAL. Procurement attempts PO now: expect 409 and zero PO records.
7. Approver reviews matrix and approves with comment. Still PENDING_APPROVAL awaiting finance. Duplicate decision is rejected. Finance approves senior level; status APPROVED.
8. Procurement issues PO. Check snapshot vendor, items, taxes and total 121540. Print preview. Duplicate PO must fail. Refresh and confirm values unchanged.
9. Record partial delivery, then DELIVERED on/after PO date. Finance records invoice 130000. A mismatch warning must appear. Upload invoice document before closing.
10. Finance records a meaningful discrepancy review and closes. Status CLOSED. Further fulfilment/upload changes fail.
11. Open audit; verify every critical event, actor/time, approval level/comment, document SHA-256 and closure reason. Download the document and compare hash with `Get-FileHash -Algorithm SHA256`.
12. Finance opens Operations. Check health, counters and user role administration. Requester cannot read metrics/profiles.

Repeat lower-total purchase to confirm only level 1 is required; test rejection, inactive vendor, missing price history and an unauthorized requester opening a foreign request.

Record each result with actual/expected, screenshot/request ID and pass/fail. Automated fixture evidence is supplied; real Supabase browser acceptance is still to be performed by the team.
