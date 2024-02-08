"""Add available modules and features in ucb

Revision ID: 21bd6f9579da
Revises: 104cc4c3e37b
Create Date: 2024-02-07 08:37:15.023907

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy import Enum

# revision identifiers, used by Alembic.
revision: str = '21bd6f9579da'
down_revision: Union[str, None] = '104cc4c3e37b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('user_company_branch',
                  sa.Column('accessible_modules', sa.ARRAY(Enum('Modules', name='modules')), nullable=True))
    op.add_column('user_company_branch',
                  sa.Column('accessible_features', sa.ARRAY(Enum('Features', name='features')), nullable=True))


def downgrade() -> None:
    op.drop_column('user_company_branch', 'accessible_modules')
    op.drop_column('user_company_branch', 'accessible_features')
