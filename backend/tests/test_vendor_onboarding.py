from sqlalchemy import select
from app.models.entities import Vendor

PREFIX = "/api/v1"

def ok(response, status=200):
    assert response.status_code == status, response.text
    return response.json()

def application_payload(email="onboarding-acme@example.com", tax_id="27ABCDE1234F1Z5"):
    return {
        "legal_name": "Acme Technology Private Limited",
        "trading_name": "Acme Technology",
        "contact_name": "Aarav Shah",
        "email": email,
        "phone": "+91 9876543210",
        "tax_id": tax_id,
        "registration_number": "U72900MH2026PTC123456",
        "address": "Mumbai, Maharashtra, India",
        "categories": "IT hardware, networking",
        "website": "https://example.com",
        "years_in_business": 4,
        "notes": "Enterprise laptop and network equipment supplier.",
        "declaration": True,
    }

def test_supplier_application_approval_creates_provisional_vendor(env):
    c, login, _ = env
    application = ok(c.post(PREFIX + "/vendor-applications", json=application_payload()), 201)
    assert application["status"] == "PENDING"
    assert application["application_number"].startswith("SUP-")

    access = ok(c.post(PREFIX + "/vendor-access-check", json={"email": "onboarding-acme@example.com"}))
    assert access["eligible"] is False

    login("procurement")
    applications = ok(c.get(PREFIX + "/vendor-applications"))
    item = next(x for x in applications if x["id"] == application["id"])
    assert item["tax_id"] == "27ABCDE1234F1Z5"

    approved = ok(
        c.post(
            PREFIX + f"/vendor-applications/{application['id']}/decision",
            json={"decision": "APPROVED", "comment": "GST and registration details reviewed and supplier approved."},
        )
    )
    assert approved["status"] == "APPROVED"
    assert approved["vendor"]["active"] is True

    vendor_id = approved["vendor"]["id"]
    risk = ok(c.get(PREFIX + f"/vendors/{vendor_id}/risk"))
    assert risk["band"] == "NEW_VENDOR"
    assert risk["score"] is None
    assert risk["history_status"] == "PROVISIONAL"

    access = ok(c.post(PREFIX + "/vendor-access-check", json={"email": "onboarding-acme@example.com"}))
    assert access["eligible"] is True

def test_rejected_supplier_application_does_not_create_vendor(env):
    c, login, sessions = env
    email = "rejected-supplier@example.com"
    application = ok(
        c.post(PREFIX + "/vendor-applications", json=application_payload(email=email, tax_id="29ABCDE9999F1Z1")),
        201,
    )
    login("procurement")
    reviewed = ok(
        c.post(
            PREFIX + f"/vendor-applications/{application['id']}/decision",
            json={"decision": "REJECTED", "comment": "Required supplier verification could not be completed."},
        )
    )
    assert reviewed["status"] == "REJECTED"
    assert reviewed["vendor"] is None
    with sessions.begin() as db:
        assert db.scalar(select(Vendor).where(Vendor.email == email)) is None

def test_duplicate_pending_supplier_application_is_blocked(env):
    c, _, _ = env
    payload = application_payload(email="duplicate-application@example.com", tax_id="27ABCDE7777F1Z2")
    ok(c.post(PREFIX + "/vendor-applications", json=payload), 201)
    response = c.post(PREFIX + "/vendor-applications", json=payload)
    assert response.status_code == 409

def test_supplier_can_track_pending_application(env):
    c, _, _ = env
    email = "track-pending@example.com"
    created = ok(c.post(PREFIX + "/vendor-applications", json=application_payload(email=email, tax_id="27ABCDE5544F1Z4")), 201)
    tracked = ok(c.post(PREFIX + "/vendor-applications/track", json={"application_number": created["application_number"], "email": email}))
    assert tracked["status"] == "PENDING"
    assert tracked["portal_access"] is False
    assert tracked["performance"] is None
    assert tracked["review_comment"] is None
    wrong = c.post(PREFIX + "/vendor-applications/track", json={"application_number": created["application_number"], "email": "someone-else@example.com"})
    assert wrong.status_code == 404


def test_supplier_tracking_updates_after_approval(env):
    c, login, _ = env
    email = "track-approved@example.com"
    created = ok(c.post(PREFIX + "/vendor-applications", json=application_payload(email=email, tax_id="27ABCDE6644F1Z8")), 201)
    login("procurement")
    ok(c.post(PREFIX + f"/vendor-applications/{created['id']}/decision", json={"decision": "APPROVED", "comment": "Business registration verified. Approved for provisional supplier onboarding."}))
    tracked = ok(c.post(PREFIX + "/vendor-applications/track", json={"application_number": created["application_number"], "email": email}))
    assert tracked["status"] == "APPROVED"
    assert tracked["portal_access"] is True
    assert tracked["performance"]["lifecycle"] == "PROVISIONAL"
    assert tracked["performance"]["band"] == "NEW_VENDOR"
    assert tracked["performance"]["score"] is None
    assert "Approved for provisional" in tracked["review_comment"]


def test_supplier_tracking_updates_after_rejection(env):
    c, login, _ = env
    email = "track-rejected@example.com"
    created = ok(c.post(PREFIX + "/vendor-applications", json=application_payload(email=email, tax_id="27ABCDE7744F1Z9")), 201)
    login("procurement")
    ok(c.post(PREFIX + f"/vendor-applications/{created['id']}/decision", json={"decision": "REJECTED", "comment": "Submitted registration details could not be verified."}))
    tracked = ok(c.post(PREFIX + "/vendor-applications/track", json={"application_number": created["application_number"], "email": email}))
    assert tracked["status"] == "REJECTED"
    assert tracked["portal_access"] is False
    assert tracked["vendor"] is None
    assert tracked["review_comment"] == "Submitted registration details could not be verified."
