import jwt
import httpx
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.models.entities import Profile, Vendor


bearer = HTTPBearer(auto_error=False)


def _supabase_claims(token: str):
    if not settings.supabase_url or not settings.anon_key:
        raise HTTPException(status_code=503, detail="Supabase Auth is not configured")

    try:
        response = httpx.get(
            f"{settings.supabase_url}/auth/v1/user",
            headers={
                "apikey": settings.anon_key,
                "Authorization": f"Bearer {token}",
            },
            timeout=10.0,
        )
    except httpx.RequestError:
        raise HTTPException(status_code=503, detail="Authentication service unavailable")

    if response.status_code != 200:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired bearer token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = response.json()
    return {
        "sub": user["id"],
        "email": user.get("email"),
        "provider": "supabase",
    }


def _local_claims(token: str):
    if not settings.local_auth_secret:
        raise HTTPException(status_code=503, detail="Local authentication is not configured")

    try:
        claims = jwt.decode(
            token,
            settings.local_auth_secret,
            algorithms=["HS256"],
            issuer="smart-procurement-local",
        )
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=401,
            detail="Local session expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=401,
            detail="Invalid local bearer token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if claims.get("provider") != "local" or not claims.get("email"):
        raise HTTPException(status_code=401, detail="Invalid local authentication claims")

    return {
        "sub": claims.get("sub"),
        "email": claims["email"],
        "provider": "local",
    }


def verify_token(token: str):
    provider = settings.auth_provider

    if provider == "local":
        return _local_claims(token)

    if provider == "supabase":
        return _supabase_claims(token)

    if provider == "auto":
        # A locally-issued token is attempted first. If it is not one of ours,
        # fall through to Supabase. This makes provider migration/testing easier.
        try:
            return _local_claims(token)
        except HTTPException as local_error:
            if local_error.status_code == 503 and not settings.supabase_url:
                raise
            return _supabase_claims(token)

    raise HTTPException(status_code=503, detail="Unsupported AUTH_PROVIDER configuration")


def current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer),
    db: Session = Depends(get_db, scope="function"),
):
    if not credentials:
        raise HTTPException(
            status_code=401,
            detail="Bearer token required",
            headers={"WWW-Authenticate": "Bearer"},
        )

    claims = verify_token(credentials.credentials)
    email = (claims.get("email") or "").lower()

    if claims["provider"] == "local":
        # Local auth deliberately resolves the existing application profile by
        # email. This lets the same Profile work with Supabase and local auth
        # without replacing the stored Supabase identity.
        user = db.scalar(select(Profile).where(Profile.email == email))
    else:
        user = db.scalar(
            select(Profile).where(Profile.supabase_user_id == claims["sub"])
        )

    vendor = db.scalar(select(Vendor).where(Vendor.email == email)) if email else None

    if not user:
        if not email:
            raise HTTPException(status_code=403, detail="An email identity is required")

        identity = (
            claims["sub"]
            if claims["provider"] == "supabase"
            else f"local:{email}"
        )

        user = Profile(
            supabase_user_id=identity,
            email=email,
            name=vendor.name if vendor else email.split("@")[0],
            role="vendor" if vendor and vendor.active else "requester",
        )
        db.add(user)
        db.flush()
    elif vendor and vendor.active and user.role == "requester":
        user.role = "vendor"
        user.name = vendor.name
        db.flush()

    if not user.active:
        raise HTTPException(status_code=403, detail="Account disabled")

    return user


def roles(*allowed):
    def check(user=Depends(current_user)):
        if user.role not in allowed:
            raise HTTPException(
                status_code=403,
                detail="Your role is not permitted to perform this action",
            )
        return user

    return check
