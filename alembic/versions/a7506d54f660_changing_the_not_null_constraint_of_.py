"""Changing the not null constraint of user_id field of 'user_company_branch'table to true

Revision ID: a7506d54f660
Revises: 8ff3542b0b6c
Create Date: 2024-02-02 17:24:49.186374

"""
from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = 'a7506d54f660'
down_revision: Union[str, None] = '8ff3542b0b6c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column('user_company_branch', 'user_id', nullable=False)


def downgrade() -> None:
    op.alter_column('user_company_branch', 'user_id', nullable=False)
