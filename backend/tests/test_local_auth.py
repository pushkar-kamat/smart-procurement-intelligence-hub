from sqlalchemy import select

from app.core.config import settings
from app.core.local_auth import hash_password
from app.models.entities import LocalCredential, Profile

PREFIX = "/api/v1"


def ok(response, status=200):
    assert response.status_code == status, response.text
    return response.json()


def test_local_login_issues_working_token(env, monkeypatch):
    c, _, sessions = env
    monkeypatch.setattr(settings, "auth_provider", "local")
    monkeypatch.setattr(settings, "local_auth_secret", "test-local-secret-1234567890-abcdefghijklmnopqrstuvwxyz")

    with sessions.begin() as db:
        profile = db.scalar(select(Profile).where(Profile.email == "requester@procure.com"))
        db.add(
            LocalCredential(
                profile_id=profile.id,
                password_hash=hash_password("Procure123"),
                active=True,
            )
        )

    login = ok(
        c.post(
            PREFIX + "/auth/local/login",
            json={"email": "requester@procure.com", "password": "Procure123"},
        )
    )
    assert login["token_type"] == "bearer"
    assert login["access_token"]

    me = ok(
        c.get(
            PREFIX + "/me",
            headers={"Authorization": "Bearer " + login["access_token"]},
        )
    )
    assert me["email"] == "requester@procure.com"
    assert me["role"] == "requester"


def test_local_password_is_hashed_and_bad_login_rejected(env, monkeypatch):
    c, _, sessions = env
    monkeypatch.setattr(settings, "auth_provider", "local")
    monkeypatch.setattr(settings, "local_auth_secret", "test-local-secret-1234567890-abcdefghijklmnopqrstuvwxyz")

    with sessions.begin() as db:
        profile = db.scalar(select(Profile).where(Profile.email == "requester@procure.com"))
        encoded = hash_password("Procure123")
        assert "Procure123" not in encoded
        db.add(
            LocalCredential(
                profile_id=profile.id,
                password_hash=encoded,
                active=True,
            )
        )

    response = c.post(
        PREFIX + "/auth/local/login",
        json={"email": "requester@procure.com", "password": "WrongPassword123"},
    )
    assert response.status_code == 401


def test_approved_vendor_can_create_local_account(env, monkeypatch):
    c, _, sessions = env
    monkeypatch.setattr(settings, "auth_provider", "local")
    monkeypatch.setattr(settings, "local_auth_secret", "test-local-secret-1234567890-abcdefghijklmnopqrstuvwxyz")

    created = ok(
        c.post(
            PREFIX + "/auth/local/signup",
            json={
                "email": "vendor@procure.com",
                "password": "Procure123",
                "portal": "vendor",
            },
        ),
        201,
    )
    assert created["user"]["role"] == "vendor"

    with sessions() as db:
        profile = db.scalar(select(Profile).where(Profile.email == "vendor@procure.com"))
        credential = db.scalar(
            select(LocalCredential).where(LocalCredential.profile_id == profile.id)
        )
        assert credential is not None
        assert "Procure123" not in credential.password_hash
