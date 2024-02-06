"""making default salary aas zero in user finance for all users

Revision ID: 3b27f6b61ac9
Revises: 8398d1014fd2
Create Date: 2024-02-06 19:46:44.873894

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import text

# revision identifiers, used by Alembic.
revision: str = '3b27f6b61ac9'
down_revision: Union[str, None] = 'a7506d54f660'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column("user_finance","salary",server_default=text('0'))


def downgrade() -> None:
    op.alter_column("user_finance","salary",server_default=None)
