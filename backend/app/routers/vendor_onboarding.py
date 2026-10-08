from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.auth import roles
from app.core.database import get_db
from app.models.entities import Vendor, VendorApplication, VendorHistory, now
from app.schemas.contracts import VendorAccessCheck, VendorApplicationDecision, VendorApplicationIn, VendorApplicationTrack
from app.services.workflow import audit, fetch, row, risk_for

router = APIRouter(prefix="/api/v1")
DB = Depends(get_db, scope="function")
PROC = Depends(roles("procurement"))

def application_view(db: Session, application: VendorApplication):
    result = row(application)
    result["vendor"] = row(db.get(Vendor, application.vendor_id)) if application.vendor_id else None
    return result

@router.post("/vendor-applications", status_code=201)
def submit_vendor_application(data: VendorApplicationIn, db: Session = DB):
    email = data.email.lower()
    tax_id = data.tax_id.upper()
    if db.scalar(select(Vendor).where(func.lower(Vendor.email) == email, Vendor.active == True)):
        raise HTTPException(409, "This supplier email is already registered. Use the vendor portal.")
    existing = db.scalar(
        select(VendorApplication).where(
            VendorApplication.status.in_(("PENDING", "APPROVED")),
            ((func.lower(VendorApplication.email) == email) | (func.upper(VendorApplication.tax_id) == tax_id)),
        )
    )
    if existing:
        raise HTTPException(409, "An active supplier application already exists for this email or tax registration ID")

    values = data.model_dump(exclude={"declaration"})
    values["email"] = email
    values["tax_id"] = tax_id
    application = VendorApplication(
        application_number=f"SUP-{now().year}-{uuid4().hex[:6].upper()}",
        **values,
    )
    db.add(application)
    db.flush()
    audit(db, None, "SUPPLIER_APPLICATION_SUBMITTED", entity=application, details={"status": "PENDING"})
    db.flush()
    return {
        "id": application.id,
        "application_number": application.application_number,
        "legal_name": application.legal_name,
        "email": application.email,
        "status": application.status,
        "submitted_at": application.submitted_at,
    }

@router.post("/vendor-applications/track")
def track_vendor_application(data: VendorApplicationTrack, db: Session = DB):
    application = db.scalar(
        select(VendorApplication).where(
            func.upper(VendorApplication.application_number) == data.application_number.strip().upper(),
            func.lower(VendorApplication.email) == data.email.strip().lower(),
        )
    )
    if not application:
        raise HTTPException(404, "No supplier application matched that reference and business email")

    vendor = db.get(Vendor, application.vendor_id) if application.vendor_id else None
    risk = risk_for(db, vendor.id) if vendor else None

    return {
        "application_number": application.application_number,
        "legal_name": application.legal_name,
        "trading_name": application.trading_name,
        "email": application.email,
        "categories": application.categories,
        "status": application.status,
        "submitted_at": application.submitted_at,
        "reviewed_at": application.reviewed_at,
        "review_comment": application.review_comment if application.status in ("APPROVED", "REJECTED") else None,
        "portal_access": bool(vendor and vendor.active and application.status == "APPROVED"),
        "vendor": (
            {"id": vendor.id, "name": vendor.name, "active": vendor.active}
            if vendor else None
        ),
        "performance": (
            {
                "lifecycle": risk.get("history_status"),
                "band": risk.get("band"),
                "score": risk.get("score"),
                "total_orders": risk.get("total_orders", 0),
            }
            if risk else None
        ),
    }


@router.post("/vendor-access-check")
def vendor_access_check(data: VendorAccessCheck, db: Session = DB):
    vendor = db.scalar(
        select(Vendor).where(func.lower(Vendor.email) == data.email.lower(), Vendor.active == True)
    )
    return {
        "eligible": bool(vendor),
        "message": (
            "Approved supplier profile found. You can create your portal account."
            if vendor
            else "No approved supplier profile was found for this email. Submit or wait for procurement review first."
        ),
    }

@router.get("/vendor-applications")
def vendor_applications(db: Session = DB, user=PROC):
    applications = list(db.scalars(select(VendorApplication).order_by(VendorApplication.submitted_at.desc())))
    applications.sort(key=lambda item: 0 if item.status == "PENDING" else 1)
    return [application_view(db, item) for item in applications]

@router.post("/vendor-applications/{id}/decision")
def decide_vendor_application(id: int, data: VendorApplicationDecision, db: Session = DB, user=PROC):
    application = fetch(db, VendorApplication, id)
    if application.status != "PENDING":
        raise HTTPException(409, "This supplier application has already been reviewed")

    vendor = None
    if data.decision == "APPROVED":
        desired_name = (application.trading_name or application.legal_name).strip()
        vendor = db.scalar(select(Vendor).where(func.lower(Vendor.email) == application.email.lower()))
        name_conflict = db.scalar(select(Vendor).where(func.lower(Vendor.name) == desired_name.lower()))
        if name_conflict and (vendor is None or name_conflict.id != vendor.id):
            raise HTTPException(409, "A different vendor already uses this supplier name")

        if vendor:
            vendor.name = desired_name
            vendor.contact = (application.contact_name + " | " + application.phone)[:80]
            vendor.active = True
        else:
            vendor = Vendor(
                name=desired_name,
                email=application.email.lower(),
                contact=(application.contact_name + " | " + application.phone)[:80],
                active=True,
            )
            db.add(vendor)
            db.flush()

        history = db.scalar(select(VendorHistory).where(VendorHistory.vendor_id == vendor.id))
        if not history:
            db.add(VendorHistory(vendor_id=vendor.id))
        application.vendor_id = vendor.id

    application.status = data.decision
    application.reviewed_at = now()
    application.reviewer_id = user.id
    application.review_comment = data.comment
    audit(
        db,
        user,
        "SUPPLIER_APPLICATION_" + data.decision,
        entity=application,
        details={"vendor_id": application.vendor_id, "comment": data.comment},
    )
    db.flush()
    return application_view(db, application)
