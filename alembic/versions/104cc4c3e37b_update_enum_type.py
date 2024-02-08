"""Update enum type

Revision ID: 104cc4c3e37b
Revises: 3b27f6b61ac9
Create Date: 2024-02-07 07:39:41.083709

"""
from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = '104cc4c3e37b'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("DROP TYPE IF EXISTS modules CASCADE")
    op.execute("DROP TYPE IF EXISTS features CASCADE")

    op.execute("CREATE TYPE modules AS ENUM ('HR', 'ACCOUNTING', 'INVOICE', 'INVENTORY', 'POS')")
    op.execute(
        "CREATE TYPE features AS ENUM ('HR_MARK_ATTENDANCE', 'HR_PENDING_APPROVAL', 'HR_TOTAL_EMPLOYEES', 'HR_SALARY_ROLLOUT', 'HR_ADD_NEW_EMPLOYEE', 'HR_VIEW_ALL_EMPLOYEES', 'HR_APPLY_LEAVES', 'HR_MY_LEAVES', 'HR_TIMESHEET')")


def downgrade() -> None:
    op.execute("DROP TYPE IF EXISTS modules")
    op.execute("DROP TYPE IF EXISTS features")
