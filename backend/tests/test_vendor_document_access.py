"""Vendor document download permissions: ownership, role, and integrity."""
from sqlalchemy import select
from app.core.auth import current_user
from app.main import app
from app.models.entities import Profile, Vendor
from test_system import prepare, ok, PREFIX

def test_vendor_own_quotation_pdf_download_and_other_vendor_forbidden(env):
    client, login, sessions = env
    _, requisition, quotation, _ = prepare(env)
    content = b'%PDF-1.4\nOwned vendor quotation evidence\n%%EOF'
    document = ok(client.post(
        PREFIX + f"/quotations/{quotation['id']}/file",
        files={'file': ('vendor.pdf', content, 'application/pdf')},
    ), 201)

    login('vendor')
    own = client.get(PREFIX + f"/documents/{document['id']}")
    assert own.status_code == 200, own.text
    assert own.content == content
    assert own.headers['x-document-sha256'] == document['sha256']

    # Create a valid second vendor login. It must never access the first
    # vendor's quotation document, even for the same requisition.
    with sessions.begin() as db:
        other_vendor = db.get(Vendor, 2)
        other_user = Profile(
            supabase_user_id='test-vendor-two',
            email=other_vendor.email,
            name='Second Vendor',
            role='vendor',
        )
        db.add(other_user)
    app.dependency_overrides[current_user] = lambda: other_user
    forbidden = client.get(PREFIX + f"/documents/{document['id']}")
    assert forbidden.status_code == 403

    # Existing staff access must continue working.
    login('procurement')
    assert client.get(PREFIX + f"/documents/{document['id']}").content == content

    # An unrelated requester cannot use the staff branch to bypass scope.
    login('other')
    assert client.get(PREFIX + f"/documents/{document['id']}").status_code == 403
