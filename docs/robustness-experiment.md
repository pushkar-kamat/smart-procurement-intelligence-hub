# Reproducible robustness experiment
## Unauthorized approval
From `backend`:
```bash
python -m pytest tests/test_system.py::test_unauthorized_approval_leaves_state_unchanged -v
```
The fixture creates/submits a requisition, invites and quotes, marks comparison ready and sends for approval. It changes the test identity to requester, calls the actual approval API, asserts 403 and verifies state remains PENDING_APPROVAL. The same run checks failed-authorization counters. This is a controlled API test, not a claim of a live Supabase session.

For deployed confirmation, obtain a requester access token from your signed-in session and keep it private:
```powershell
$headers = @{ Authorization = "Bearer $env:REQUESTER_TOKEN" }
$body = @{ decision = 'APPROVED'; comment = 'Unauthorized approval experiment' } | ConvertTo-Json
Invoke-RestMethod "$env:API_URL/api/v1/requisitions/$env:REQ_ID/approval" -Method Post -Headers $headers -ContentType 'application/json' -Body $body
```
Expected 403. Read the request before/after with the same authorized requester and verify unchanged status. Capture only status, timestamp and request ID, never the token. Delete local screenshots containing credentials.

## Additional experiments
- `test_role_and_state_guards`: PO before approval → 409, no PO row.
- `test_invalid_quotation_duplicate_invite_and_locked_quote`: negative unit price → 422; no committed alteration.
- `test_bad_file_and_foreign_document`: fake PDF → 422; foreign requester document access → 403.
- `test_tampered_file_fails_integrity`: storage bytes modified → 409.
- `test_storage_failure_rolls_back_and_missing_file_is_controlled`: storage throws 503; no document row, state retained.
- `test_file_size_limit`: over-limit bytes → 413.

Actual local automated results: see `evidence/pytest.txt` and `build-and-test-report.md`. Live deployment result, tester and evidence link: **not yet measured**. No destructive experiment should run against real documents.
