"""Risk-based approval policy threshold.

Revision ID: g5c2d3
Revises: f4b1c2
"""
from alembic import op

revision = "g5c2d3"
down_revision = "f4b1c2"
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        """
        UPDATE approval_rules
        SET min_amount = 200000
        WHERE required_role = 'finance_admin' AND level = 2
        """
    )


def downgrade():
    op.execute(
        """
        UPDATE approval_rules
        SET min_amount = 100000
        WHERE required_role = 'finance_admin' AND level = 2
        """
    )
