"""
Painel Administrativo — acesso restrito a superadmins.
Métricas, usuários, assinaturas, logs.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.core.database import get_db
from app.core.middleware.auth import get_current_user
from app.shared.models import User, Document, TaxEvent, AIInteraction, AuditLog, SubscriptionPlan

router = APIRouter(prefix="/admin", tags=["Admin"])

# Emails com acesso admin (configurar via env em produção)
ADMIN_EMAILS = {"admin@canmos-niti.com.br"}


def require_admin(current_user: User = Depends(get_current_user)) -> User:
    if current_user.email not in ADMIN_EMAILS:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acesso restrito")
    return current_user


@router.get("/metrics")
def get_metrics(db: Session = Depends(get_db), _=Depends(require_admin)):
    """Métricas gerais da plataforma."""
    total_users = db.query(func.count(User.id)).scalar()
    premium_users = db.query(func.count(User.id)).filter(
        User.subscription_plan != SubscriptionPlan.FREE
    ).scalar()
    total_docs = db.query(func.count(Document.id)).scalar()
    total_tax_events = db.query(func.count(TaxEvent.id)).scalar()
    total_ai_chats = db.query(func.count(AIInteraction.id)).scalar()

    # Distribuição de planos
    planos = db.query(User.subscription_plan, func.count(User.id)).group_by(
        User.subscription_plan
    ).all()

    return {
        "usuarios": {
            "total": total_users,
            "premium": premium_users,
            "free": total_users - premium_users,
            "taxa_conversao": round((premium_users / total_users * 100), 1) if total_users else 0,
        },
        "documentos": {"total": total_docs},
        "tax_events": {"total": total_tax_events},
        "ai_chats": {"total": total_ai_chats},
        "planos": {str(p): c for p, c in planos},
    }


@router.get("/users")
def list_users(
    page: int = 1,
    limit: int = 50,
    db: Session = Depends(get_db),
    _=Depends(require_admin),
):
    offset = (page - 1) * limit
    users = db.query(User).order_by(User.created_at.desc()).offset(offset).limit(limit).all()
    total = db.query(func.count(User.id)).scalar()

    return {
        "total": total,
        "page": page,
        "users": [
            {
                "id": str(u.id),
                "nome": u.nome,
                "email": u.email,
                "plano": u.subscription_plan,
                "status": u.status,
                "documentos": len(u.documents),
                "created_at": u.created_at.isoformat(),
            }
            for u in users
        ],
    }


@router.get("/users/{user_id}")
def get_user_detail(
    user_id: str,
    db: Session = Depends(get_db),
    _=Depends(require_admin),
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    docs = db.query(func.count(Document.id)).filter(Document.user_id == user.id).scalar()
    events = db.query(func.count(TaxEvent.id)).filter(TaxEvent.user_id == user.id).scalar()
    chats = db.query(func.count(AIInteraction.id)).filter(AIInteraction.user_id == user.id).scalar()

    return {
        "id": str(user.id),
        "nome": user.nome,
        "email": user.email,
        "cpf": user.cpf,
        "plano": user.subscription_plan,
        "status": user.status,
        "stripe_customer_id": user.stripe_customer_id,
        "lgpd_consent": user.lgpd_consent,
        "created_at": user.created_at.isoformat(),
        "stats": {"documentos": docs, "tax_events": events, "ai_chats": chats},
    }


@router.get("/logs")
def get_audit_logs(
    page: int = 1,
    limit: int = 100,
    db: Session = Depends(get_db),
    _=Depends(require_admin),
):
    offset = (page - 1) * limit
    logs = db.query(AuditLog).order_by(AuditLog.created_at.desc()).offset(offset).limit(limit).all()
    total = db.query(func.count(AuditLog.id)).scalar()

    return {
        "total": total,
        "logs": [
            {
                "id": str(l.id),
                "user_id": str(l.user_id) if l.user_id else None,
                "action": l.action,
                "entity": l.entity,
                "ip_address": l.ip_address,
                "created_at": l.created_at.isoformat(),
            }
            for l in logs
        ],
    }
