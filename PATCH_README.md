# Smart Procurement Vendor Portal + RFQ Patch

This patch is designed for the current staged/main BCA-08 Smart Procurement repository.

## What changes

- Adds a new `vendor` application role.
- Adds a vendor portal with an RFQ inbox and performance dashboard.
- Procurement can broadcast an RFQ to all active vendors with one action.
- Invited vendors submit their own quotations; procurement no longer needs to enter them in the UI.
- Vendor quotations automatically appear in the procurement requisition/comparison workflow.
- Vendors cannot see competing vendors' quotations or staff-only requisition/comparison APIs.
- Adds optional quotation-document upload from the vendor portal.
- Adds three established demo vendors with historical performance:
  - Vertex Equipment — Low risk baseline
  - Northstar Technologies — Medium risk baseline
  - Bluebell Networks — High risk baseline
- Keeps new vendors neutral: no history means `INSUFFICIENT_HISTORY`, not High risk.
- Restores default departments and market price history idempotently.
- Leaves new-vendor onboarding out of the main UI for now; existing vendor details can still be edited.

## Apply to Windows project

1. Make sure your current branch is clean.

```cmd
git status
```

2. Create a feature branch before applying the patch.

```cmd
git switch -c feature/vendor-portal-rfq
```

3. Extract this ZIP directly into the repository root:

```text
C:\smart-procurement-staged
```

Choose **Replace the files in the destination**.

4. Apply the database migration.

```cmd
cd C:\smart-procurement-staged\backend
.venv\Scripts\activate
alembic upgrade head
```

5. Add/update the established vendor data, departments, price history and approval rules.

```cmd
python -m app.seed_vendor_marketplace
```

The seed is idempotent and can safely be run again. It does not delete existing vendors.

6. Create/link the three vendor Supabase demo accounts. Use the same local demo password policy you already use for the other demo identities.

```cmd
set DEMO_PASSWORD=<your existing demo password>
python -m app.seed_users
```

Vendor login emails created/linked by the script:

```text
vendor.vertex@example.com
vendor.northstar@example.com
vendor.bluebell@example.com
```

7. Restart the backend and frontend.

Backend:

```cmd
cd C:\smart-procurement-staged\backend
.venv\Scripts\activate
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Frontend in another terminal:

```cmd
cd C:\smart-procurement-staged\frontend
npm run dev
```

## Verify

Backend tests:

```cmd
cd C:\smart-procurement-staged\backend
python -m pytest -q
```

Expected for this patch baseline:

```text
27 passed
```

Frontend build:

```cmd
cd C:\smart-procurement-staged\frontend
npm run build
```

## Demo workflow

1. Requester creates and submits a requisition.
2. Procurement opens the requisition and clicks **Send RFQ to all active vendors**.
3. Sign in as one of the vendor demo accounts.
4. Open **RFQ inbox** and submit the quotation.
5. Repeat with other vendor accounts.
6. Sign back in as procurement.
7. Open the requisition: vendor-submitted quotations are already present.
8. Generate the comparison and compare price, lead time, anomaly evidence and vendor history.
9. Select the preferred vendor and continue approval → PO → delivery → invoice.

## Cold-start/new-vendor behavior

A new vendor with no completed history is intentionally shown as:

```text
INSUFFICIENT_HISTORY / Not scored
```

The system does not label the vendor High risk merely because historical data is missing. Procurement must use quotation and verification evidence until enough completed history is available.

## Important

The RFQ notification in this patch is an **in-app vendor portal notification/inbox**, not an email or SMS notification. External notifications can be added later without changing the core quotation workflow.
