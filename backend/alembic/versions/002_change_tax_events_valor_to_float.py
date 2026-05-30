"""change tax_events.valor from String to Float

Revision ID: 002
Revises: 001
Create Date: 2026-05-25
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "002"
down_revision: Union[str, None] = "001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column(
        "tax_events",
        "valor",
        type_=sa.Float(),
        postgresql_using="valor::double precision",
    )


def downgrade() -> None:
    op.alter_column(
        "tax_events",
        "valor",
        type_=sa.String(50),
        postgresql_using="valor::varchar(50)",
    )
