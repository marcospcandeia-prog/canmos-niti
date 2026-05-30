from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.core.database import get_db
from app.core.middleware.auth import get_current_user
from app.shared.models import User, AIInteraction, Document, TaxEvent
from .service import chat_tributario, chat_tributario_stream, build_user_context

router = APIRouter(prefix="/ai", tags=["IA Tributária"])


class ChatRequest(BaseModel):
    pergunta: str
    stream: bool = False


@router.post("/chat")
def chat(
    req: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    documents = db.query(Document).filter(Document.user_id == current_user.id).all()
    tax_events = db.query(TaxEvent).filter(TaxEvent.user_id == current_user.id).all()
    ctx, docs_resumo = build_user_context(current_user, tax_events, documents)

    if req.stream:
        def generator():
            resposta_completa = []
            for token in chat_tributario_stream(req.pergunta, ctx, docs_resumo):
                resposta_completa.append(token)
                yield token
            # Salvar no banco
            _save_interaction(current_user.id, req.pergunta, "".join(resposta_completa), db)

        return StreamingResponse(generator(), media_type="text/plain")

    resposta = chat_tributario(req.pergunta, ctx, docs_resumo)
    _save_interaction(current_user.id, req.pergunta, resposta, db)

    return {"resposta": resposta, "modelo": "ollama/" + __import__("app.core.config", fromlist=["settings"]).settings.OLLAMA_MODEL}


@router.get("/history")
def history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    interactions = db.query(AIInteraction).filter(
        AIInteraction.user_id == current_user.id
    ).order_by(AIInteraction.created_at.desc()).limit(50).all()

    return [
        {
            "id": str(i.id),
            "pergunta": i.pergunta,
            "resposta": i.resposta,
            "created_at": i.created_at.isoformat(),
        }
        for i in interactions
    ]


def _save_interaction(user_id, pergunta: str, resposta: str, db: Session):
    interaction = AIInteraction(
        user_id=user_id,
        pergunta=pergunta,
        resposta=resposta,
        modelo_ia=__import__("app.core.config", fromlist=["settings"]).settings.OLLAMA_MODEL,
    )
    db.add(interaction)
    db.commit()
