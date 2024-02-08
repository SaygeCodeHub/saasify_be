"""Add module_name in module_subscription table

Revision ID: 364bf6fd5bda
Revises: 21bd6f9579da
Create Date: 2024-02-08 11:12:30.105952

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import Enum

# revision identifiers, used by Alembic.
revision: str = '364bf6fd5bda'
down_revision: Union[str, None] = '21bd6f9579da'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('module_subscriptions',
                  sa.Column('module_name', Enum('Modules', name='modules'), nullable=True))


def downgrade() -> None:
    op.drop_column('module_subscriptions', 'module_name')
