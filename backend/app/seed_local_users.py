"""Create/update local demo credentials without using Supabase."""
import os

from sqlalchemy import func, select

from app.core.database import SessionLocal
from app.core.local_auth import hash_password
from app.models.entities import Department, LocalCredential, Profile, Vendor


PASSWORD = os.getenv("DEMO_PASSWORD", "Procure123")

STAFF = [
    ("requester@procure.com", "requester", "Demo Requester"),
    ("procurement@procure.com", "procurement", "Procurement Officer"),
    ("approver@procure.com", "approver", "Purchase Approver"),
    ("finance@procure.com", "finance_admin", "Finance Administrator"),
]


def ensure_profile(db, email, role, name, department_id=None):
    profile = db.scalar(
        select(Profile).where(func.lower(Profile.email) == email.lower())
    )
    if not profile:
        profile = Profile(
            supabase_user_id=f"local-demo:{email}",
            email=email,
            name=name,
            role=role,
            department_id=department_id,
            active=True,
        )
        db.add(profile)
        db.flush()
    else:
        profile.name = name
        profile.role = role
        profile.active = True
        if role == "requester" and department_id and not profile.department_id:
            profile.department_id = department_id
    return profile


def set_password(db, profile):
    credential = db.scalar(
        select(LocalCredential).where(LocalCredential.profile_id == profile.id)
    )
    encoded = hash_password(PASSWORD)
    if credential:
        credential.password_hash = encoded
        credential.active = True
    else:
        db.add(
            LocalCredential(
                profile_id=profile.id,
                password_hash=encoded,
                active=True,
            )
        )


def main():
    if len(PASSWORD) < 8:
        raise SystemExit("DEMO_PASSWORD must contain at least 8 characters")

    with SessionLocal.begin() as db:
        department = db.scalar(
            select(Department).where(Department.name == "Information Technology")
        )
        department_id = department.id if department else None

        for email, role, name in STAFF:
            profile = ensure_profile(
                db,
                email,
                role,
                name,
                department_id if role == "requester" else None,
            )
            set_password(db, profile)
            print(email, role, "local access enabled")

        # Give every active seeded/demo vendor a local vendor login too.
        for vendor in db.scalars(select(Vendor).where(Vendor.active == True)):
            profile = db.scalar(
                select(Profile).where(func.lower(Profile.email) == vendor.email.lower())
            )
            if not profile:
                profile = Profile(
                    supabase_user_id=f"local-vendor:{vendor.id}",
                    email=vendor.email.lower(),
                    name=vendor.name,
                    role="vendor",
                    active=True,
                )
                db.add(profile)
                db.flush()
            else:
                profile.name = vendor.name
                profile.role = "vendor"
                profile.active = True
            set_password(db, profile)

    print("")
    print("Local authentication demo users are ready.")
    print("Demo password:", PASSWORD)


if __name__ == "__main__":
    main()
