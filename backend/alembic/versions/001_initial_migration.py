"""initial migration

Revision ID: 001
Revises:
Create Date: 2024-01-15
"""
from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

from alembic import op

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("uuid", UUID(as_uuid=True), nullable=True),
        sa.Column("nome", sa.String(200), nullable=False),
        sa.Column("cpf", sa.String(11), nullable=False),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("telefone", sa.String(20), nullable=True),
        sa.Column("senha_hash", sa.String(255), nullable=False),
        sa.Column("status", sa.Enum("active", "inactive", "blocked", name="userstatus"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("uuid"),
    )
    op.create_index(op.f("ix_users_cpf"), "users", ["cpf"], unique=True)
    op.create_index(op.f("ix_users_email"), "users", ["email"], unique=True)

    op.create_table(
        "user_profiles",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("user_id", sa.String(), nullable=False),
        sa.Column("profissao", sa.String(200), nullable=True),
        sa.Column("estado_civil", sa.String(50), nullable=True),
        sa.Column("possui_dependentes", sa.String(5), nullable=True),
        sa.Column("possui_investimentos", sa.String(5), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_user_profiles_user_id"), "user_profiles", ["user_id"])

    op.create_table(
        "documents",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("user_id", sa.String(), nullable=False),
        sa.Column("tipo", sa.Enum("infr", "dirf", "carnepr", "comprovante", "extrato", "outro", name="documenttype"), nullable=True),
        sa.Column("nome_original", sa.String(500), nullable=False),
        sa.Column("storage_path", sa.String(1000), nullable=False),
        sa.Column("mime_type", sa.String(100), nullable=True),
        sa.Column("hash_arquivo", sa.String(64), nullable=True),
        sa.Column("tamanho_bytes", sa.String(20), nullable=True),
        sa.Column("status", sa.Enum("pending", "processing", "completed", "error", name="documentstatus"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_documents_user_id"), "documents", ["user_id"])

    op.create_table(
        "ocr_results",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("document_id", sa.String(), nullable=False),
        sa.Column("texto_extraido", sa.Text(), nullable=True),
        sa.Column("confianca", sa.Float(), nullable=True),
        sa.Column("engine_utilizada", sa.String(50), nullable=True),
        sa.Column("status", sa.String(20), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_ocr_results_document_id"), "ocr_results", ["document_id"])

    op.create_table(
        "tax_events",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("user_id", sa.String(), nullable=False),
        sa.Column("document_id", sa.String(), nullable=False),
        sa.Column("categoria", sa.String(100), nullable=True),
        sa.Column("subcategoria", sa.String(100), nullable=True),
        sa.Column("valor", sa.String(50), nullable=True),
        sa.Column("competencia", sa.String(7), nullable=True),
        sa.Column("origem", sa.String(200), nullable=True),
        sa.Column("metadata_json", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_tax_events_user_id"), "tax_events", ["user_id"])

    op.create_table(
        "declarations",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("user_id", sa.String(), nullable=False),
        sa.Column("ano_base", sa.String(4), nullable=False),
        sa.Column("status", sa.Enum("draft", "pending", "completed", "filed", name="declarationstatus"), nullable=True),
        sa.Column("restituicao_estimada", sa.Float(), nullable=True),
        sa.Column("imposto_devido", sa.Float(), nullable=True),
        sa.Column("total_rendimentos", sa.Float(), nullable=True),
        sa.Column("total_retencao", sa.Float(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_declarations_user_id"), "declarations", ["user_id"])

    op.create_table(
        "validations",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("declaration_id", sa.String(), nullable=False),
        sa.Column("tipo", sa.String(100), nullable=True),
        sa.Column("severidade", sa.Enum("info", "warning", "error", "critical", name="validationseverity"), nullable=True),
        sa.Column("mensagem", sa.Text(), nullable=True),
        sa.Column("metadata_json", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_validations_declaration_id"), "validations", ["declaration_id"])

    op.create_table(
        "ai_interactions",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("user_id", sa.String(), nullable=False),
        sa.Column("pergunta", sa.Text(), nullable=True),
        sa.Column("resposta", sa.Text(), nullable=True),
        sa.Column("modelo_ia", sa.String(50), nullable=True),
        sa.Column("contexto", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_ai_interactions_user_id"), "ai_interactions", ["user_id"])

    op.create_table(
        "audit_logs",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("user_id", sa.String(), nullable=False),
        sa.Column("action", sa.String(100), nullable=False),
        sa.Column("entity", sa.String(100), nullable=True),
        sa.Column("entity_id", sa.String(100), nullable=True),
        sa.Column("metadata_json", sa.JSON(), nullable=True),
        sa.Column("ip_address", sa.String(45), nullable=True),
        sa.Column("user_agent", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_audit_logs_user_id"), "audit_logs", ["user_id"])


def downgrade() -> None:
    op.drop_table("audit_logs")
    op.drop_table("ai_interactions")
    op.drop_table("validations")
    op.drop_table("declarations")
    op.drop_table("tax_events")
    op.drop_table("ocr_results")
    op.drop_table("documents")
    op.drop_table("user_profiles")
    op.drop_table("users")

    op.execute("DROP TYPE IF EXISTS userstatus")
    op.execute("DROP TYPE IF EXISTS documenttype")
    op.execute("DROP TYPE IF EXISTS documentstatus")
    op.execute("DROP TYPE IF EXISTS declarationstatus")
    op.execute("DROP TYPE IF EXISTS validationseverity")
