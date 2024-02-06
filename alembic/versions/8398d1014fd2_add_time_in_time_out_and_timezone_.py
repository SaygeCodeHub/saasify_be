"""Add time_in, time_out and timezone columns in branch_seetings table

Revision ID: 8398d1014fd2
Revises: a7506d54f660
Create Date: 2024-02-06 12:39:44.787389

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import text

# revision identifiers, used by Alembic.
revision: str = '8398d1014fd2'
down_revision: Union[str, None] = 'a7506d54f660'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("branch_settings", sa.Column("time_in", sa.DateTime(timezone=True), nullable=True))
    op.add_column("branch_settings", sa.Column("time_out", sa.DateTime(timezone=True), nullable=True))
    op.add_column("branch_settings",
                  sa.Column("timezone", sa.DateTime(timezone=True), server_default=text("(now() AT TIME ZONE 'IST')"),
                            nullable=True))


def downgrade() -> None:
    op.drop_column("branch_settings", "time_in")
    op.drop_column("branch_settings", "time_out")
    op.drop_column("branch_settings", "timezone")
