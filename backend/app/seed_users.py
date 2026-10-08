"""Demo identity migration/seed utility for the local classroom project."""
import os

import httpx
from sqlalchemy import select

from app.core.config import settings
from app.core.database import SessionLocal
from app.models.entities import Profile, Vendor


ACCOUNTS = [
    ("requester@procure.com", "requester", "Demo Requester"),
    ("procurement@procure.com", "procurement", "Procurement Officer"),
    ("approver@procure.com", "approver", "Purchase Approver"),
    ("finance@procure.com", "finance_admin", "Finance Administrator"),
    ("vendor.vertex@procure.com", "vendor", "Vertex Equipment"),
    ("vendor.northstar@procure.com", "vendor", "Northstar Technologies"),
    ("vendor.bluebell@procure.com", "vendor", "Bluebell Networks"),
    ("vendor.cedar@procure.com", "vendor", "Cedar Office Systems"),
    ("vendor.harbor@procure.com", "vendor", "Harbor Business Supply"),
    ("vendor.metro@procure.com", "vendor", "Metro Digital Works"),
    ("vendor.summit@procure.com", "vendor", "Summit Workspace"),
    ("vendor.juniper@procure.com", "vendor", "Juniper Stationery"),
    ("vendor.pioneer@procure.com", "vendor", "Pioneer Electronics"),
    ("vendor.newleaf@procure.com", "vendor", "New Leaf Supplies"),
]


def legacy_email(new_email: str) -> str:
    return new_email.replace("@procure.com", "@example.com")


def main():
    password = os.getenv("DEMO_PASSWORD", "Procure123")
    if len(password) < 8:
        raise SystemExit("Set DEMO_PASSWORD to at least 8 characters.")
    if not settings.service_key or not settings.supabase_url:
        raise SystemExit(
            "Set SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY locally before running this utility."
        )

    headers = {
        "apikey": settings.service_key,
        "Authorization": "Bearer " + settings.service_key,
    }

    with (
        httpx.Client(
            base_url=settings.supabase_url + "/auth/v1",
            headers=headers,
            timeout=30,
        ) as client,
        SessionLocal.begin() as db,
    ):
        identities = {}
        page = 1
        while True:
            response = client.get("/admin/users", params={"page": page, "per_page": 100})
            response.raise_for_status()
            users = response.json().get("users", [])
            identities.update(
                {u["email"].lower(): u for u in users if u.get("email")}
            )
            if len(users) < 100:
                break
            page += 1

        for email, role, name in ACCOUNTS:
            old_email = legacy_email(email)
            identity = identities.get(email.lower())
            legacy = identities.get(old_email.lower())

            if identity:
                response = client.put(
                    f"/admin/users/{identity['id']}",
                    json={"password": password, "email_confirm": True},
                )
                response.raise_for_status()
                identity = response.json()
                action = "updated"
            elif legacy:
                response = client.put(
                    f"/admin/users/{legacy['id']}",
                    json={
                        "email": email,
                        "password": password,
                        "email_confirm": True,
                    },
                )
                response.raise_for_status()
                identity = response.json()
                action = "migrated"
            else:
                response = client.post(
                    "/admin/users",
                    json={
                        "email": email,
                        "password": password,
                        "email_confirm": True,
                    },
                )
                response.raise_for_status()
                identity = response.json()
                action = "created"

            profile = db.scalar(
                select(Profile).where(Profile.email.in_([email, old_email]))
            )
            if not profile:
                profile = Profile(email=email, name=name)
                db.add(profile)

            profile.email = email
            profile.supabase_user_id = identity["id"]
            profile.role = role
            profile.name = name
            profile.active = True

            if role == "vendor":
                vendor = db.scalar(
                    select(Vendor).where(Vendor.email.in_([email, old_email]))
                )
                if vendor:
                    vendor.email = email

            print(email, role, action)

        # Local DB cleanup for any remaining seeded legacy-domain rows.
        for profile in db.scalars(
            select(Profile).where(Profile.email.like("%@example.com"))
        ):
            profile.email = profile.email.replace("@example.com", "@procure.com")

        for vendor in db.scalars(
            select(Vendor).where(Vendor.email.like("%@example.com"))
        ):
            vendor.email = vendor.email.replace("@example.com", "@procure.com")

    print("")
    print("Demo accounts are ready on @procure.com.")
    print("Demo password:", password)


if __name__ == "__main__":
    main()
