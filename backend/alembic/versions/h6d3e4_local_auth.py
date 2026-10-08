"""Add local authentication credentials.

Revision ID: h6d3e4
Revises: g5c2d3
"""
from alembic import op
import sqlalchemy as sa


revision = "h6d3e4"
down_revision = "g5c2d3"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "local_credentials",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("profile_id", sa.Integer(), sa.ForeignKey("profiles.id"), nullable=False, unique=True),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("last_login_at", sa.DateTime(timezone=True), nullable=True),
    )

    if op.get_bind().dialect.name == "postgresql":
        op.execute(sa.text('ALTER TABLE "local_credentials" ENABLE ROW LEVEL SECURITY'))


def downgrade():
    op.drop_table("local_credentials")
