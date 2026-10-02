import httpx
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.models.entities import Profile


bearer = HTTPBearer(auto_error=False)


def verify_token(token):
    if not settings.supabase_url or not settings.anon_key:
        raise HTTPException(
            status_code=503,
            detail="Supabase Auth is not configured"
        )

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
        raise HTTPException(
            status_code=503,
            detail="Authentication service unavailable"
        )

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
    }


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

    user = db.scalar(
        select(Profile).where(
            Profile.supabase_user_id == claims["sub"]
        )
    )

    if not user:
        email = claims.get("email")

        if not email:
            raise HTTPException(
                status_code=403,
                detail="An email identity is required"
            )

        user = Profile(
            supabase_user_id=claims["sub"],
            email=email,
            name=email.split("@")[0],
            role="requester",
        )

        db.add(user)
        db.flush()

    if not user.active:
        raise HTTPException(
            status_code=403,
            detail="Account disabled"
        )

    return user


def roles(*allowed):
    def check(user=Depends(current_user)):
        if user.role not in allowed:
            raise HTTPException(
                status_code=403,
                detail="Your role is not permitted to perform this action"
            )
        return user

    return check