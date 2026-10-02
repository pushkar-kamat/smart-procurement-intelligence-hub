"""Prevent Supabase Data API bypass of backend authorization."""
from alembic import op
import sqlalchemy as sa
revision='7bfa01'
down_revision='2305dc836ec3'
branch_labels=None
depends_on=None
TABLES=['departments','profiles','vendors','requisitions','requisition_items','vendor_invitations','quotations','quotation_items','price_history','vendor_history','approval_rules','approvals','purchase_orders','deliveries','invoices','documents','audit_logs']
def upgrade():
    if op.get_bind().dialect.name=='postgresql':
        for table in TABLES:
            op.execute(sa.text(f'ALTER TABLE "{table}" ENABLE ROW LEVEL SECURITY'))
        # No client policies. Browser clients must use FastAPI, not PostgREST.
        # The database owner used by the API/migration connection bypasses RLS.
def downgrade():
    if op.get_bind().dialect.name=='postgresql':
        for table in TABLES:op.execute(sa.text(f'ALTER TABLE "{table}" DISABLE ROW LEVEL SECURITY'))
