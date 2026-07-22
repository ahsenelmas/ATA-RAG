"""Change embedding dimension to 384

Revision ID: e3b9c61f908c
Revises: b7e9a5673498
Create Date: 2026-07-22 13:56:41.764344

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e3b9c61f908c'
down_revision: Union[str, Sequence[str], None] = 'b7e9a5673498'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        "ALTER TABLE chunks "
        "ALTER COLUMN embedding TYPE vector(384) "
        "USING NULL"
    )


def downgrade() -> None:
    op.execute(
        "ALTER TABLE chunks "
        "ALTER COLUMN embedding TYPE vector(1536) "
        "USING NULL"
    )
