"""create column 'deduction' in user_finance table

Revision ID: 8ff3542b0b6c
Revises: 
Create Date: 2024-02-01 13:53:28.784232

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy import text

# revision identifiers, used by Alembic.
revision: str = '8ff3542b0b6c'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("user_finance", sa.Column('deduction', sa.Double, nullable=True, server_default=text('0')))


def downgrade() -> None:
    op.drop_column("user_finance", 'deduction')
