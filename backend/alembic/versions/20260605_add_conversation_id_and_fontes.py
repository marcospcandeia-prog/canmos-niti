"""Add conversation_id and fontes_consultadas to ai_interactions

Revision ID: 002_add_ai_fields
Revises: 001_initial
Create Date: 2026-06-05 22:30:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '002_add_ai_fields'
down_revision: Union[str, None] = '001_initial'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('ai_interactions', sa.Column('conversation_id', sa.String(length=36), nullable=True))
    op.add_column('ai_interactions', sa.Column('fontes_consultadas', sa.Text(), nullable=True))
    op.create_index('ix_ai_interactions_conversation_id', 'ai_interactions', ['conversation_id'])


def downgrade() -> None:
    op.drop_index('ix_ai_interactions_conversation_id', table_name='ai_interactions')
    op.drop_column('ai_interactions', 'fontes_consultadas')
    op.drop_column('ai_interactions', 'conversation_id')
