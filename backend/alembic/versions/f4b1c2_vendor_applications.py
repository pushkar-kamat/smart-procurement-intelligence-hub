"""Add supplier onboarding applications.

Revision ID: f4b1c2
Revises: d8a2f0
"""
from alembic import op
import sqlalchemy as sa

revision = "f4b1c2"
down_revision = "d8a2f0"
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        "vendor_applications",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("application_number", sa.String(length=32), nullable=False, unique=True),
        sa.Column("legal_name", sa.String(length=120), nullable=False),
        sa.Column("trading_name", sa.String(length=120), nullable=True, server_default=""),
        sa.Column("contact_name", sa.String(length=120), nullable=False),
        sa.Column("email", sa.String(length=254), nullable=False),
        sa.Column("phone", sa.String(length=40), nullable=False),
        sa.Column("tax_id", sa.String(length=60), nullable=False),
        sa.Column("registration_number", sa.String(length=80), nullable=False),
        sa.Column("address", sa.String(length=500), nullable=False),
        sa.Column("categories", sa.String(length=500), nullable=False),
        sa.Column("website", sa.String(length=200), nullable=True, server_default=""),
        sa.Column("years_in_business", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("notes", sa.String(length=1000), nullable=True, server_default=""),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="PENDING"),
        sa.Column("submitted_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("reviewer_id", sa.Integer(), sa.ForeignKey("profiles.id"), nullable=True),
        sa.Column("review_comment", sa.String(length=2000), nullable=True),
        sa.Column("vendor_id", sa.Integer(), sa.ForeignKey("vendors.id"), nullable=True, unique=True),
        sa.CheckConstraint("status IN ('PENDING','APPROVED','REJECTED')", name="ck_vendor_application_status"),
    )
    op.create_index("ix_vendor_applications_email", "vendor_applications", ["email"])
    op.create_index("ix_vendor_applications_tax_id", "vendor_applications", ["tax_id"])
    op.create_index("ix_vendor_applications_status", "vendor_applications", ["status"])

def downgrade():
    op.drop_index("ix_vendor_applications_status", table_name="vendor_applications")
    op.drop_index("ix_vendor_applications_tax_id", table_name="vendor_applications")
    op.drop_index("ix_vendor_applications_email", table_name="vendor_applications")
    op.drop_table("vendor_applications")
