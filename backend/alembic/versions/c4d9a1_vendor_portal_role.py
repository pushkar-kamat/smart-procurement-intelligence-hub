"""Add vendor application role.

Revision ID: c4d9a1
Revises: 7bfa01
"""
from alembic import op
import sqlalchemy as sa

revision='c4d9a1'
down_revision='7bfa01'
branch_labels=None
depends_on=None


def upgrade():
    bind=op.get_bind()
    if bind.dialect.name=='postgresql':
        op.execute(sa.text('ALTER TABLE profiles DROP CONSTRAINT IF EXISTS profiles_role_check'))
        op.execute(sa.text("ALTER TABLE profiles ADD CONSTRAINT profiles_role_check CHECK (role IN ('requester','procurement','approver','finance_admin','vendor'))"))


def downgrade():
    bind=op.get_bind()
    if bind.dialect.name=='postgresql':
        op.execute(sa.text("UPDATE profiles SET role='requester' WHERE role='vendor'"))
        op.execute(sa.text('ALTER TABLE profiles DROP CONSTRAINT IF EXISTS profiles_role_check'))
        op.execute(sa.text("ALTER TABLE profiles ADD CONSTRAINT profiles_role_check CHECK (role IN ('requester','procurement','approver','finance_admin'))"))
