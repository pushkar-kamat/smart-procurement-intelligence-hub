from typing import Literal

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.auth import current_user
from app.core.database import get_db
from app.core.local_auth import create_access_token, hash_password, verify_password
from app.models.entities import LocalCredential, Profile, Vendor, now


router = APIRouter(prefix="/api/v1/auth/local", tags=["local-auth"])
DB = Depends(get_db, scope="function")


class LocalLoginIn(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    email: str = Field(min_length=3, max_length=254)
    password: str = Field(min_length=8, max_length=128)


class LocalSignupIn(LocalLoginIn):
    portal: Literal["requester", "vendor"] = "requester"


class LocalPasswordChange(BaseModel):
    model_config = ConfigDict(extra="forbid")
    password: str = Field(min_length=8, max_length=128)


def _session(profile: Profile):
    return {
        "access_token": create_access_token(profile),
        "token_type": "bearer",
        "expires_in": 60 * 60 * 8,
        "user": {
            "id": profile.id,
            "email": profile.email,
            "name": profile.name,
            "role": profile.role,
        },
    }


@router.post("/login")
def local_login(data: LocalLoginIn, db: Session = DB):
    email = data.email.lower()
    profile = db.scalar(select(Profile).where(func.lower(Profile.email) == email))
    if not profile or not profile.active:
        raise HTTPException(401, "Invalid email or password")

    credential = db.scalar(
        select(LocalCredential).where(LocalCredential.profile_id == profile.id)
    )
    if not credential or not credential.active:
        raise HTTPException(
            401,
            "Local login is not enabled for this account. Use Supabase sign in or ask the administrator to enable local access.",
        )

    if not verify_password(data.password, credential.password_hash):
        raise HTTPException(401, "Invalid email or password")

    credential.last_login_at = now()
    return _session(profile)


@router.post("/signup", status_code=201)
def local_signup(data: LocalSignupIn, db: Session = DB):
    email = data.email.lower()

    existing_profile = db.scalar(
        select(Profile).where(func.lower(Profile.email) == email)
    )
    if existing_profile:
        existing_credential = db.scalar(
            select(LocalCredential).where(
                LocalCredential.profile_id == existing_profile.id
            )
        )
        if existing_credential:
            raise HTTPException(409, "A local account already exists for this email")

    vendor = db.scalar(
        select(Vendor).where(
            func.lower(Vendor.email) == email,
            Vendor.active == True,
        )
    )

    if data.portal == "vendor":
        if not vendor:
            raise HTTPException(
                403,
                "Supplier access requires a Procurement-approved active vendor profile",
            )
        role = "vendor"
        name = vendor.name
    else:
        if vendor:
            raise HTTPException(
                409,
                "This email belongs to an approved supplier. Use the vendor portal.",
            )
        role = "requester"
        name = email.split("@")[0]

    if existing_profile:
        # Never let public signup convert privileged staff accounts.
        if existing_profile.role not in ("requester", "vendor"):
            raise HTTPException(403, "This staff account cannot be registered through public signup")
        profile = existing_profile
        profile.role = role
        profile.name = name
        profile.active = True
    else:
        profile = Profile(
            supabase_user_id=f"local:{email}",
            email=email,
            name=name,
            role=role,
            active=True,
        )
        db.add(profile)
        db.flush()

    credential = LocalCredential(
        profile_id=profile.id,
        password_hash=hash_password(data.password),
        active=True,
    )
    db.add(credential)
    db.flush()

    return _session(profile)


@router.post("/change-password")
def local_change_password(
    data: LocalPasswordChange,
    db: Session = DB,
    user=Depends(current_user),
):
    credential = db.scalar(
        select(LocalCredential).where(LocalCredential.profile_id == user.id)
    )
    if not credential:
        credential = LocalCredential(
            profile_id=user.id,
            password_hash=hash_password(data.password),
            active=True,
        )
        db.add(credential)
    else:
        credential.password_hash = hash_password(data.password)
        credential.active = True
    return {"status": "ok"}
