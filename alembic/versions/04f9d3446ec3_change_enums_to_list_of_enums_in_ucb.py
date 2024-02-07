"""change enums to List of enums in ucb

Revision ID: 04f9d3446ec3
Revises: 21bd6f9579da
Create Date: 2024-02-07 08:56:03.965409

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy import Enum

# revision identifiers, used by Alembic.
revision: str = '04f9d3446ec3'
down_revision: Union[str, None] = '21bd6f9579da'
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
