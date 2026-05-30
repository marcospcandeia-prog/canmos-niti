"""Initial schema — CANMOS-NITI

Revision ID: 001_initial
Revises:
Create Date: 2026-05-29
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ── users ─────────────────────────────────────────────
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("nome", sa.String(200), nullable=False),
        sa.Column("cpf", sa.String(11), nullable=True),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("telefone", sa.String(20), nullable=True),
        sa.Column("senha_hash", sa.String(255), nullable=False),
        sa.Column("status", sa.Enum("active","inactive","suspended", name="userstatus"), nullable=False, server_default="active"),
        sa.Column("subscription_plan", sa.Enum("free","premium_monthly","premium_annual", name="subscriptionplan"), nullable=False, server_default="free"),
        sa.Column("stripe_customer_id", sa.String(255), nullable=True),
        sa.Column("stripe_subscription_id", sa.String(255), nullable=True),
        sa.Column("lgpd_consent", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("lgpd_consent_at", sa.String(50), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
        sa.UniqueConstraint("cpf"),
    )
    op.create_index("ix_users_email", "users", ["email"])
    op.create_index("ix_users_cpf", "users", ["cpf"])

    # ── user_profiles ─────────────────────────────────────
    op.create_table(
        "user_profiles",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("profissao", sa.String(100), nullable=True),
        sa.Column("estado_civil", sa.String(50), nullable=True),
        sa.Column("possui_dependentes", sa.Boolean(), server_default="false"),
        sa.Column("possui_investimentos", sa.Boolean(), server_default="false"),
        sa.Column("possui_imoveis", sa.Boolean(), server_default="false"),
        sa.Column("possui_mei", sa.Boolean(), server_default="false"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id"),
    )

    # ── documents ─────────────────────────────────────────
    op.create_table(
        "documents",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tipo", sa.Enum(
            "informe_rendimentos","recibo_medico","despesa_educacao",
            "extrato_bancario","extrato_corretora","darf","nota_fiscal","outros",
            name="documenttype"), nullable=False, server_default="outros"),
        sa.Column("nome_original", sa.String(500), nullable=False),
        sa.Column("storage_path", sa.String(1000), nullable=False),
        sa.Column("mime_type", sa.String(100), nullable=False),
        sa.Column("hash_arquivo", sa.String(64), nullable=False),
        sa.Column("tamanho_bytes", sa.String(20), nullable=True),
        sa.Column("status", sa.Enum(
            "uploaded","processing","ocr_done","classified","tax_events_created","error",
            name="documentstatus"), nullable=False, server_default="uploaded"),
        sa.Column("ano_base", sa.String(4), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_documents_user_id", "documents", ["user_id"])

    # ── ocr_results ───────────────────────────────────────
    op.create_table(
        "ocr_results",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("document_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("texto_extraido", sa.Text(), nullable=True),
        sa.Column("confianca", sa.Float(), nullable=True),
        sa.Column("engine_utilizada", sa.Enum("paddleocr","tesseract", name="ocrengine"), nullable=True),
        sa.Column("status", sa.Enum("pending","processing","done","error", name="ocrstatus"), nullable=False, server_default="pending"),
        sa.Column("erro_msg", sa.String(500), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["document_id"], ["documents.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("document_id"),
    )

    # ── tax_events ────────────────────────────────────────
    op.create_table(
        "tax_events",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("document_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("categoria", sa.Enum(
            "rendimento_tributavel","rendimento_isento","deducao_medica",
            "deducao_educacao","deducao_dependente","retencao_fonte",
            "investimento","imovel","outros",
            name="taxcategory"), nullable=False),
        sa.Column("subcategoria", sa.String(100), nullable=True),
        sa.Column("valor", sa.Numeric(15, 2), nullable=False),
        sa.Column("competencia", sa.String(7), nullable=True),
        sa.Column("origem", sa.String(200), nullable=True),
        sa.Column("fonte_pagadora", sa.String(200), nullable=True),
        sa.Column("cnpj_fonte", sa.String(14), nullable=True),
        sa.Column("ano_base", sa.String(4), nullable=True),
        sa.Column("metadata_json", postgresql.JSONB(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["document_id"], ["documents.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_tax_events_user_id", "tax_events", ["user_id"])

    # ── ai_interactions ───────────────────────────────────
    op.create_table(
        "ai_interactions",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("pergunta", sa.Text(), nullable=False),
        sa.Column("resposta", sa.Text(), nullable=True),
        sa.Column("modelo_ia", sa.String(100), nullable=True),
        sa.Column("contexto", sa.String(200), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_ai_interactions_user_id", "ai_interactions", ["user_id"])

    # ── audit_logs ────────────────────────────────────────
    op.create_table(
        "audit_logs",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("action", sa.String(100), nullable=False),
        sa.Column("entity", sa.String(100), nullable=True),
        sa.Column("entity_id", sa.String(100), nullable=True),
        sa.Column("ip_address", sa.String(50), nullable=True),
        sa.Column("metadata_json", postgresql.JSONB(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_audit_logs_user_id", "audit_logs", ["user_id"])


def downgrade() -> None:
    op.drop_table("audit_logs")
    op.drop_table("ai_interactions")
    op.drop_table("tax_events")
    op.drop_table("ocr_results")
    op.drop_table("documents")
    op.drop_table("user_profiles")
    op.drop_table("users")
    for enum in ["userstatus","subscriptionplan","documenttype","documentstatus","ocrengine","ocrstatus","taxcategory"]:
        sa.Enum(name=enum).drop(op.get_bind(), checkfirst=True)
