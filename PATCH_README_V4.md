# Smart Procurement UI Patch V4

This cumulative patch builds on the vendor/RFQ and V2/V3 improvements already applied.

## V4 changes

- Replaces the visual system with a monochrome black / white / gray palette in both light and dark modes.
- Removes visible academic/project labels such as BCA, capstone and prototype wording from the product UI.
- Restyles native select controls with a custom monochrome chevron, rounded surface, hover and focus states so dropdown fields no longer look like browser defaults.
- Moves the Registered supplier / Vendor portal access control from the left hero area to directly below the Team Access sign-in panel.
- Keeps staff and vendor login routes separate (`/login` and `/vendor-login`).
- Keeps all earlier vendor history, RFQ, approval-context, delivery-date, role, authentication and password improvements.

## Apply

Extract this ZIP into the project root and replace existing files.

For the current project:

```cmd
cd C:\smart-procurement-staged\frontend
npm run build
npm run dev
```

No new database migration is required specifically for the V4 visual changes. If applying this cumulative ZIP to a checkout that has not received the earlier vendor patches, also run the migrations and seed steps described in the previous patch instructions.

## Quick visual checks

- Light mode uses white, off-white and gray only.
- Dark mode uses black, charcoal, white and gray only.
- Primary actions invert between black-on-light and white-on-dark.
- Status chips remain distinguishable through shade/border/label rather than green/gold accents.
- Staff login shows `TEAM ACCESS`; the Registered supplier link is directly below that card content.
- Vendor login remains a dedicated page.
