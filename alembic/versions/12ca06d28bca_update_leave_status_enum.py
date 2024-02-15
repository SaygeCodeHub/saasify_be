"""update leave status enum

Revision ID: 12ca06d28bca
Revises: 364bf6fd5bda
Create Date: 2024-02-15 14:16:08.919157

"""
from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = '12ca06d28bca'
down_revision: Union[str, None] = '364bf6fd5bda'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("ALTER TYPE LeaveStatus ADD VALUE 'WITHDRAW';")


def downgrade() -> None:
    pass
