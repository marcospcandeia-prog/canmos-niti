"""Initial schema

Revision ID: 001_initial
Revises: 
Create Date: 2026-06-03 22:30:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSONB


# revision identifiers, used by Alembic.
revision: str = '001_initial'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('uuid', UUID(as_uuid=True), nullable=False),
        sa.Column('nome', sa.String(length=255), nullable=False),
        sa.Column('cpf', sa.String(length=11), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('telefone', sa.String(length=20), nullable=True),
        sa.Column('senha_hash', sa.String(length=255), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False, server_default='active'),
        sa.Column('lgpd_consent_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_users_id', 'users', ['id'])
    op.create_index('ix_users_uuid', 'users', ['uuid'], unique=True)
    op.create_index('ix_users_cpf', 'users', ['cpf'], unique=True)
    op.create_index('ix_users_email', 'users', ['email'], unique=True)

    # Create user_profiles table
    op.create_table(
        'user_profiles',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('profissao', sa.String(length=255), nullable=True),
        sa.Column('estado_civil', sa.String(length=50), nullable=True),
        sa.Column('possui_dependentes', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('possui_investimentos', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id')
    )
    op.create_index('ix_user_profiles_id', 'user_profiles', ['id'])

    # Create documents table
    op.create_table(
        'documents',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('tipo', sa.String(length=100), nullable=True),
        sa.Column('nome_original', sa.String(length=255), nullable=False),
        sa.Column('storage_path', sa.String(length=500), nullable=False),
        sa.Column('mime_type', sa.String(length=100), nullable=False),
        sa.Column('hash_arquivo', sa.String(length=64), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='uploaded'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_documents_id', 'documents', ['id'])
    op.create_index('ix_documents_user_id', 'documents', ['user_id'])
    op.create_index('ix_documents_hash_arquivo', 'documents', ['hash_arquivo'])

    # Create ocr_results table
    op.create_table(
        'ocr_results',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('document_id', sa.Integer(), nullable=False),
        sa.Column('texto_extraido', sa.Text(), nullable=True),
        sa.Column('confianca', sa.Float(), nullable=True),
        sa.Column('engine_utilizada', sa.String(length=50), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='pending'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.ForeignKeyConstraint(['document_id'], ['documents.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('document_id')
    )
    op.create_index('ix_ocr_results_id', 'ocr_results', ['id'])
    op.create_index('ix_ocr_results_document_id', 'ocr_results', ['document_id'], unique=True)

    # Create tax_events table
    op.create_table(
        'tax_events',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('document_id', sa.Integer(), nullable=True),
        sa.Column('categoria', sa.String(length=100), nullable=False),
        sa.Column('subcategoria', sa.String(length=100), nullable=True),
        sa.Column('valor', sa.Numeric(precision=15, scale=2), nullable=False),
        sa.Column('competencia', sa.String(length=7), nullable=False),
        sa.Column('origem', sa.String(length=50), nullable=False, server_default='ocr'),
        sa.Column('metadata_json', JSONB(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['document_id'], ['documents.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_tax_events_id', 'tax_events', ['id'])
    op.create_index('ix_tax_events_user_id', 'tax_events', ['user_id'])
    op.create_index('ix_tax_events_document_id', 'tax_events', ['document_id'])
    op.create_index('ix_tax_events_categoria', 'tax_events', ['categoria'])
    op.create_index('ix_tax_events_competencia', 'tax_events', ['competencia'])

    # Create declarations table
    op.create_table(
        'declarations',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('ano_base', sa.Integer(), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='rascunho'),
        sa.Column('restituicao_estimada', sa.Numeric(precision=15, scale=2), nullable=True),
        sa.Column('imposto_devido', sa.Numeric(precision=15, scale=2), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_declarations_id', 'declarations', ['id'])
    op.create_index('ix_declarations_user_id', 'declarations', ['user_id'])
    op.create_index('ix_declarations_ano_base', 'declarations', ['ano_base'])
    op.create_index('ix_declarations_user_ano', 'declarations', ['user_id', 'ano_base'])

    # Create validations table
    op.create_table(
        'validations',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('declaration_id', sa.Integer(), nullable=False),
        sa.Column('tipo', sa.String(length=100), nullable=False),
        sa.Column('severidade', sa.String(length=20), nullable=False, server_default='info'),
        sa.Column('mensagem', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.ForeignKeyConstraint(['declaration_id'], ['declarations.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_validations_id', 'validations', ['id'])
    op.create_index('ix_validations_declaration_id', 'validations', ['declaration_id'])

    # Create ai_interactions table
    op.create_table(
        'ai_interactions',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('pergunta', sa.Text(), nullable=False),
        sa.Column('resposta', sa.Text(), nullable=True),
        sa.Column('modelo_ia', sa.String(length=50), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_ai_interactions_id', 'ai_interactions', ['id'])
    op.create_index('ix_ai_interactions_user_id', 'ai_interactions', ['user_id'])

    # Create audit_logs table
    op.create_table(
        'audit_logs',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('action', sa.String(length=50), nullable=False),
        sa.Column('entity', sa.String(length=100), nullable=True),
        sa.Column('entity_id', sa.Integer(), nullable=True),
        sa.Column('metadata_json', JSONB(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_audit_logs_id', 'audit_logs', ['id'])
    op.create_index('ix_audit_logs_user_id', 'audit_logs', ['user_id'])
    op.create_index('ix_audit_logs_action', 'audit_logs', ['action'])
    op.create_index('ix_audit_logs_entity', 'audit_logs', ['entity'])
    op.create_index('ix_audit_logs_created_at', 'audit_logs', [sa.text('created_at DESC')])


def downgrade() -> None:
    # Drop tables in reverse order (respecting foreign keys)
    op.drop_table('audit_logs')
    op.drop_table('ai_interactions')
    op.drop_table('validations')
    op.drop_table('declarations')
    op.drop_table('tax_events')
    op.drop_table('ocr_results')
    op.drop_table('documents')
    op.drop_table('user_profiles')
    op.drop_table('users')
