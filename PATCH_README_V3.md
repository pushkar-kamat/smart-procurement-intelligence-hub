# Smart Procurement Intelligence Hub — Vendor & UX Patch V3

This is the cumulative follow-up patch for the current staged project. It retains the vendor intelligence/RFQ improvements from the earlier vendor patches and adds the latest authentication and visual redesign.

## What V3 changes

### 1. Dynamic landing experience
- Replaces the flat split-screen login with one continuous, layered finance interface.
- Adds subtle animated background geometry, floating evidence cards, and responsive motion.
- Keeps the visual hierarchy minimal rather than decorative-heavy.

### 2. Separate staff and vendor sign-in
- Staff login: `/login`
- Vendor login: `/vendor-login`
- The vendor portal is invitation-only and does not expose requester sign-up.
- Portal intent is checked against the authenticated role. Supplier accounts are redirected to the vendor experience and staff accounts are kept out of vendor access.

### 3. Neutral finance color system
Light mode is no longer green-tinted:
- warm off-white background
- neutral white cards
- graphite text
- champagne / bronze interaction accent
- green reserved for success states only

Dark mode is now:
- charcoal / slate surfaces
- champagne / bronze accent
- neutral borders and typography
- green reserved only for success states

### 4. Existing V2 improvements retained
The cumulative ZIP also contains the vendor intelligence and workflow files from V1/V2, including:
- vendor role and private supplier workspace
- RFQ distribution and vendor-submitted quotations
- established vendor historical records
- neutral new-vendor handling
- selection reasoning in approval context
- approved RFQ state
- partial-delivery date validation fix
- supplier-role repair
- password visibility, confirmation, forgot/reset password
- vendor portal tests and migrations

## Apply

Extract this ZIP directly into:

`C:\smart-procurement-staged`

Choose **Replace the files in the destination**.

Then run:

```cmd
cd C:\smart-procurement-staged\backend
.venv\Scripts\activate
alembic upgrade head
python -m app.seed_vendor_marketplace
set DEMO_PASSWORD=DemoProcure123
python -m app.seed_users
python -m pytest -q
```

Verify the frontend:

```cmd
cd C:\smart-procurement-staged\frontend
npm run build
npm run dev
```

## Sign-in routes

Staff users:

`http://localhost:5173/login`

Vendor users:

`http://localhost:5173/vendor-login`

Example supplier accounts seeded by the vendor marketplace setup:

- `vendor.vertex@example.com`
- `vendor.northstar@example.com`
- `vendor.bluebell@example.com`

Use the locally configured demo password.

## Git recommendation

Apply on a new feature branch, verify the browser flow, then commit only after tests and frontend build pass.
