from fastapi import APIRouter, Depends, Request, Header
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.core.database import get_db
from app.core.middleware.auth import get_current_user
from app.shared.models import User
from .service import (
    create_checkout_session,
    handle_webhook_event,
    get_subscription_info,
    cancel_subscription,
)

router = APIRouter(prefix="/payments", tags=["Pagamentos"])


class CheckoutRequest(BaseModel):
    plan: str  # "premium_monthly" | "premium_annual"
    success_url: str
    cancel_url: str


@router.post("/checkout")
def checkout(
    req: CheckoutRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    url = create_checkout_session(
        req.plan, current_user, req.success_url, req.cancel_url
    )
    return {"checkout_url": url}


@router.post("/webhook")
async def webhook(
    request: Request,
    stripe_signature: str = Header(None, alias="stripe-signature"),
    db: Session = Depends(get_db),
):
    payload = await request.body()
    return handle_webhook_event(payload, stripe_signature, db)


@router.get("/subscription")
def subscription_info(
    current_user: User = Depends(get_current_user),
):
    return get_subscription_info(current_user)


@router.delete("/subscription")
def cancel(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return cancel_subscription(current_user, db)
