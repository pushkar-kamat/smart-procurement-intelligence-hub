# Smart Procurement – Vendor Intelligence & UX Patch V2

This patch is designed to be extracted over the project after the earlier **Vendor Portal + RFQ Patch**.

## What this patch fixes

1. **Established vendor history**
   - Restores a 10-vendor established supplier network from the original demo concept.
   - Every established vendor receives historical order/performance statistics.
   - Common legacy aliases such as `northstar` are enriched instead of remaining history-less.
   - Established vendors can still receive a risk score when one risk denominator is unavailable; the score is normalized across available evidence and shows an evidence-coverage percentage.

2. **New-vendor cold start**
   - New suppliers are labelled `NEW_VENDOR` / provisional instead of `INSUFFICIENT_HISTORY` or high risk.
   - No historical-risk penalty is applied until at least three orders exist.

3. **Approval context and RFQ award status**
   - Procurement's vendor-selection reason is stored on the requisition.
   - Approval inbox shows selected vendor, quotation total, risk band and selection reasoning.
   - RFQ status progresses from `INVITED` → `RESPONDED` → `SELECTED_FOR_APPROVAL` → `APPROVED`.
   - Other vendors become `NOT_SELECTED` after final approval.

4. **Partial delivery date handling**
   - Purchase orders display the vendor's promised delivery date calculated from the quotation.
   - `Actual receipt date` is separated from an optional `Expected remaining delivery date` for partial deliveries.
   - A future promised/remaining date is no longer confused with an actual delivery date.

5. **Vendor role repair**
   - A verified Supabase identity whose email exactly matches a registered active vendor is automatically treated as a `vendor` rather than a requester.
   - Vendor demo profiles use company names.

6. **Separate staff and supplier workspaces**
   - Requester / Procurement / Approver / Finance use the internal procurement workspace.
   - Vendors use a separate supplier portal with only Vendor Overview and RFQ Inbox.

7. **UI refresh**
   - Dark finance theme is the default, with a Light/Dark toggle.
   - Cleaner panels, approval context, risk statistics and supplier portal treatment.
   - Custom file selector replaces the browser's plain file input UI.
   - Forms suppress browser-native "required field" popups and show application-level messages instead.

8. **Authentication UX**
   - Confirm-password field on signup.
   - Show/hide password icon.
   - Forgot-password email flow.
   - `/reset-password` screen for setting the new password.

9. **Price-history matching improvement**
   - Historical price lookup is case-insensitive, so `Business Laptop` can use history stored as `Business laptop`.

## Apply the patch

From the project root, create a feature branch first:

```cmd
cd C:\smart-procurement-staged
git switch main
git pull origin main
git switch -c feature/vendor-intelligence-ux-v2
```

Extract this ZIP directly into:

```text
C:\smart-procurement-staged
```

Choose **Replace the files in the destination**.

## Database upgrade and demo data

```cmd
cd C:\smart-procurement-staged\backend
.venv\Scripts\activate
alembic upgrade head
python -m app.seed_vendor_marketplace
```

Then link/create the demo identities:

```cmd
set DEMO_PASSWORD=DemoProcure123
python -m app.seed_users
```

Existing Supabase demo accounts keep their existing passwords. Newly created demo vendor accounts use the password supplied in `DEMO_PASSWORD`.

## Demo vendor accounts

- `vendor.vertex@example.com`
- `vendor.northstar@example.com`
- `vendor.bluebell@example.com`
- `vendor.cedar@example.com`
- `vendor.harbor@example.com`
- `vendor.metro@example.com`
- `vendor.summit@example.com`
- `vendor.juniper@example.com`
- `vendor.pioneer@example.com`
- `vendor.newleaf@example.com`

## Password-reset redirect

For local password reset, make sure Supabase Auth redirect URLs allow:

```text
http://localhost:5173/reset-password
```

For deployment, also allow your deployed frontend URL followed by `/reset-password`.

## Verify

Backend tests:

```cmd
cd C:\smart-procurement-staged\backend
python -m pytest -q
```

The patch test suite used during packaging reports **28 passed**.

Frontend production build:

```cmd
cd C:\smart-procurement-staged\frontend
npm run build
```

Then restart backend and frontend and walk through:

1. Requester submits requisition.
2. Procurement sends RFQ to active vendors.
3. Vendor submits quotation.
4. Procurement compares offers and records selection reasoning.
5. Approver sees vendor + reason + risk in approval inbox.
6. Finance completes approval; winning RFQ shows `APPROVED`.
7. Procurement issues PO; promised delivery date is displayed.
8. For partial receipt, enter today's actual receipt date and a future expected remaining-delivery date.

## Files included

- `backend/alembic/versions/d8a2f0_vendor_decision_delivery.py`
- `backend/app/core/auth.py`
- `backend/app/models/entities.py`
- `backend/app/routers/procurement.py`
- `backend/app/schemas/contracts.py`
- `backend/app/seed_users.py`
- `backend/app/seed_vendor_marketplace.py`
- `backend/app/services/intelligence.py`
- `backend/app/services/workflow.py`
- `backend/tests/test_system.py`
- `backend/tests/test_vendor_portal.py`
- `frontend/src/App.jsx`
- `frontend/src/components.jsx`
- `frontend/src/styles.css`
