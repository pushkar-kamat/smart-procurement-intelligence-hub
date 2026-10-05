"""Add vendor selection reasoning and partial-delivery expectation.

Revision ID: d8a2f0
Revises: c4d9a1
"""
from alembic import op
import sqlalchemy as sa

revision='d8a2f0'
down_revision='c4d9a1'
branch_labels=None
depends_on=None


def upgrade():
    op.add_column('requisitions', sa.Column('selection_reason', sa.String(length=2000), nullable=True))
    op.add_column('deliveries', sa.Column('expected_completion_at', sa.Date(), nullable=True))


def downgrade():
    op.drop_column('deliveries','expected_completion_at')
    op.drop_column('requisitions','selection_reason')
