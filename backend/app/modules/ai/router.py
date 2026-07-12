import logging
import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database.session import get_db
from app.core.middleware.auth import get_current_user
from app.shared.models.user import User
from app.shared.models.ai import AIInteraction
from app.modules.ai.service import TaxAssistant
from app.modules.ai.schemas import ChatRequest, ChatResponse, ConversationResponse, MessageResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ai", tags=["IA Assistente"])

_assistant: TaxAssistant = None


def get_assistant() -> TaxAssistant:
    global _assistant
    if _assistant is None:
        _assistant = TaxAssistant()
    return _assistant


@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    assistant = get_assistant()
    conversation_id = request.conversation_id or str(uuid.uuid4())

    result = await assistant.ask(request.mensagem, conversation_id, user_id=current_user.id)

    ai_interaction = AIInteraction(
        user_id=current_user.id,
        conversation_id=conversation_id,
        pergunta=request.mensagem,
        resposta=result["resposta"],
        modelo_ia="llama3.2:3b",
        fontes_consultadas="; ".join(result["fontes"]),
    )
    db.add(ai_interaction)
    await db.commit()

    return ChatResponse(
        resposta=result["resposta"],
        conversation_id=conversation_id,
        model="llama3.2:3b",
        fontes=result["fontes"],
    )


@router.get("/conversations", response_model=list[ConversationResponse])
async def list_conversations(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    stmt = (
        select(AIInteraction.conversation_id, AIInteraction.created_at)
        .where(AIInteraction.user_id == current_user.id)
        .distinct()
        .order_by(AIInteraction.created_at.desc())
        .limit(20)
    )
    result = await db.execute(stmt)
    conversations = result.all()

    return [
        ConversationResponse(
            id=c.conversation_id,
            titulo=f"Conversa {i + 1}",
            created_at=c.created_at,
            updated_at=c.created_at,
        )
        for i, c in enumerate(conversations)
    ]


@router.get("/conversations/{conversation_id}/messages", response_model=list[MessageResponse])
async def get_conversation_messages(
    conversation_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    stmt = (
        select(AIInteraction)
        .where(
            AIInteraction.user_id == current_user.id,
            AIInteraction.conversation_id == conversation_id,
        )
        .order_by(AIInteraction.created_at.asc())
    )
    result = await db.execute(stmt)
    interactions = result.scalars().all()

    messages = []
    for interaction in interactions:
        messages.append(
            MessageResponse(
                id=interaction.id * 2 - 1,
                conversation_id=conversation_id,
                role="user",
                content=interaction.pergunta,
                created_at=interaction.created_at,
            )
        )
        messages.append(
            MessageResponse(
                id=interaction.id * 2,
                conversation_id=conversation_id,
                role="assistant",
                content=interaction.resposta,
                created_at=interaction.created_at,
            )
        )

    return messages


@router.get("/health")
async def health():
    assistant = get_assistant()
    status = await assistant.check_health()
    return {"service": "ai", **status}


@router.post("/clear")
async def clear_history(
    current_user: User = Depends(get_current_user)
):
    assistant = get_assistant()
    assistant.histories.clear()
    return {"mensagem": "Historico limpo"}
