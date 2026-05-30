"""
Serviço de pagamentos — Stripe.
Fluxo: Checkout → Webhook → Ativação automática de plano.
"""
import stripe
import threading
from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.core.config import settings
from app.shared.models import User, SubscriptionPlan

stripe.api_key = settings.STRIPE_SECRET_KEY

PLANS = {
    "premium_monthly": {
        "price_id": settings.STRIPE_PRICE_PREMIUM_MONTHLY,
        "nome": "Premium Mensal",
        "plan": SubscriptionPlan.PREMIUM_MONTHLY,
    },
    "premium_annual": {
        "price_id": settings.STRIPE_PRICE_PREMIUM_ANNUAL,
        "nome": "Premium Anual",
        "plan": SubscriptionPlan.PREMIUM_ANNUAL,
    },
}


def create_checkout_session(plan_key: str, user: User, success_url: str, cancel_url: str) -> str:
    """Cria sessão de checkout Stripe e retorna a URL."""
    plan = PLANS.get(plan_key)
    if not plan:
        raise HTTPException(status_code=400, detail="Plano inválido")

    # Criar ou reusar customer Stripe
    customer_id = user.stripe_customer_id
    if not customer_id:
        customer = stripe.Customer.create(
            email=user.email,
            name=user.nome,
            metadata={"user_id": str(user.id)},
        )
        customer_id = customer.id

    session = stripe.checkout.Session.create(
        customer=customer_id,
        payment_method_types=["card"],
        line_items=[{"price": plan["price_id"], "quantity": 1}],
        mode="subscription",
        success_url=success_url + "?session_id={CHECKOUT_SESSION_ID}",
        cancel_url=cancel_url,
        metadata={"user_id": str(user.id), "plan": plan_key},
        subscription_data={"metadata": {"user_id": str(user.id), "plan": plan_key}},
    )

    return session.url


def handle_webhook_event(payload: bytes, sig_header: str, db: Session) -> dict:
    """Processa eventos do webhook Stripe."""
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except stripe.error.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Assinatura do webhook inválida")

    event_type = event["type"]

    if event_type == "checkout.session.completed":
        _on_checkout_completed(event["data"]["object"], db)

    elif event_type in ("customer.subscription.updated", "customer.subscription.created"):
        _on_subscription_updated(event["data"]["object"], db)

    elif event_type == "customer.subscription.deleted":
        _on_subscription_cancelled(event["data"]["object"], db)

    elif event_type == "invoice.payment_failed":
        _on_payment_failed(event["data"]["object"], db)

    return {"received": True, "type": event_type}


def _on_checkout_completed(session: dict, db: Session):
    user_id = session.get("metadata", {}).get("user_id")
    plan_key = session.get("metadata", {}).get("plan")
    subscription_id = session.get("subscription")

    if not user_id or not plan_key:
        return

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return

    plan_data = PLANS.get(plan_key)
    if plan_data:
        user.subscription_plan = plan_data["plan"]
        user.stripe_subscription_id = subscription_id
        if not user.stripe_customer_id:
            user.stripe_customer_id = session.get("customer")
        db.commit()
        # Email de confirmação em background
        threading.Thread(
            target=_send_payment_email,
            args=(user.email, user.nome, plan_data["nome"]),
            daemon=True,
        ).start()


def _send_payment_email(email: str, nome: str, plano: str):
    try:
        from app.modules.email.service import send_payment_confirmed
        send_payment_confirmed(email, nome, plano, "")
    except Exception:
        pass


def _on_subscription_updated(subscription: dict, db: Session):
    user_id = subscription.get("metadata", {}).get("user_id")
    if not user_id:
        return

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return

    status = subscription.get("status")
    if status == "active":
        plan_key = subscription.get("metadata", {}).get("plan", "premium_monthly")
        plan_data = PLANS.get(plan_key)
        if plan_data:
            user.subscription_plan = plan_data["plan"]
    elif status in ("canceled", "unpaid", "past_due"):
        user.subscription_plan = SubscriptionPlan.FREE

    db.commit()


def _on_subscription_cancelled(subscription: dict, db: Session):
    user_id = subscription.get("metadata", {}).get("user_id")
    if not user_id:
        return
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        user.subscription_plan = SubscriptionPlan.FREE
        user.stripe_subscription_id = None
        db.commit()


def _on_payment_failed(invoice: dict, db: Session):
    # Log apenas — não cancela imediatamente
    pass


def get_subscription_info(user: User) -> dict:
    """Retorna informações da assinatura atual."""
    if not user.stripe_subscription_id:
        return {"plan": user.subscription_plan, "status": "no_subscription"}

    try:
        sub = stripe.Subscription.retrieve(user.stripe_subscription_id)
        return {
            "plan": user.subscription_plan,
            "status": sub.status,
            "current_period_end": sub.current_period_end,
            "cancel_at_period_end": sub.cancel_at_period_end,
        }
    except Exception:
        return {"plan": user.subscription_plan, "status": "unknown"}


def cancel_subscription(user: User, db: Session) -> dict:
    """Cancela assinatura ao fim do período atual."""
    if not user.stripe_subscription_id:
        raise HTTPException(status_code=400, detail="Nenhuma assinatura ativa")

    stripe.Subscription.modify(
        user.stripe_subscription_id,
        cancel_at_period_end=True,
    )
    return {"message": "Assinatura cancelada ao fim do período atual"}
