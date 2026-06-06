"""
Users Router
FastAPI endpoints for user profile management
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database.session import get_db
from app.core.middleware.auth import get_current_user
from app.modules.auth.schemas import MessageResponse
from app.modules.users.schemas import (
    PasswordChange,
    UserProfileResponse,
    UserProfileUpdate,
    UserStats,
)
from app.modules.users.service import UsersService
from app.shared.models.user import User

router = APIRouter()


@router.get(
    "/me",
    response_model=UserProfileResponse,
    summary="Obter perfil do usuário autenticado",
    description="Retorna informações completas do perfil do usuário autenticado",
    responses={
        200: {"description": "Perfil retornado com sucesso"},
        401: {"description": "Não autenticado"},
    }
)
async def get_my_profile(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> UserProfileResponse:
    """
    Obter perfil do usuário autenticado
    
    Retorna informações completas do usuário incluindo:
    - Dados pessoais (nome, CPF, email, telefone)
    - Status da conta
    - Data de consentimento LGPD
    - Informações profissionais (profissão, estado civil)
    - Flags (possui dependentes, possui investimentos)
    """
    profile_data = await UsersService.get_user_profile(current_user, db)
    return UserProfileResponse(**profile_data)


@router.put(
    "/me",
    response_model=UserProfileResponse,
    summary="Atualizar perfil do usuário",
    description="Atualiza informações do perfil do usuário autenticado",
    responses={
        200: {"description": "Perfil atualizado com sucesso"},
        401: {"description": "Não autenticado"},
        422: {"description": "Dados inválidos"},
    }
)
async def update_my_profile(
    update_data: UserProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> UserProfileResponse:
    """
    Atualizar perfil do usuário
    
    Campos atualizáveis:
    - **nome**: Nome completo
    - **telefone**: Telefone de contato
    - **profissao**: Profissão
    - **estado_civil**: Estado civil (solteiro, casado, divorciado, viuvo)
    - **possui_dependentes**: Possui dependentes fiscais?
    - **possui_investimentos**: Possui investimentos?
    
    **Nota:** Todos os campos são opcionais. Envie apenas os que deseja atualizar.
    """
    updated_profile = await UsersService.update_user_profile(current_user, update_data, db)
    return UserProfileResponse(**updated_profile)


@router.post(
    "/me/change-password",
    response_model=MessageResponse,
    summary="Alterar senha",
    description="Altera a senha do usuário autenticado",
    responses={
        200: {"description": "Senha alterada com sucesso"},
        400: {"description": "Senha atual incorreta"},
        401: {"description": "Não autenticado"},
        422: {"description": "Senhas não conferem ou inválidas"},
    }
)
async def change_password(
    password_data: PasswordChange,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> MessageResponse:
    """
    Alterar senha
    
    - **senha_atual**: Senha atual do usuário
    - **senha_nova**: Nova senha (mínimo 8 caracteres)
    - **senha_nova_confirmacao**: Confirmação da nova senha
    
    **Validações:**
    - Senha atual deve estar correta
    - Nova senha deve ter no mínimo 8 caracteres
    - Confirmação deve ser igual à nova senha
    """
    await UsersService.change_password(current_user, password_data, db)
    return MessageResponse(message="Senha alterada com sucesso")


@router.get(
    "/me/stats",
    response_model=UserStats,
    summary="Obter estatísticas do usuário",
    description="Retorna estatísticas de uso do sistema pelo usuário autenticado",
    responses={
        200: {"description": "Estatísticas retornadas com sucesso"},
        401: {"description": "Não autenticado"},
    }
)
async def get_my_stats(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> UserStats:
    """
    Obter estatísticas do usuário
    
    Retorna:
    - **total_documents**: Total de documentos enviados
    - **documents_processed**: Documentos processados com sucesso
    - **total_tax_events**: Total de eventos tributários gerados
    - **declarations_count**: Total de declarações criadas
    - **last_activity**: Data/hora da última atividade
    """
    return await UsersService.get_user_stats(current_user, db)


@router.delete(
    "/me",
    response_model=MessageResponse,
    summary="Desativar conta",
    description="Desativa a conta do usuário (soft delete)",
    responses={
        200: {"description": "Conta desativada com sucesso"},
        401: {"description": "Não autenticado"},
    }
)
async def delete_my_account(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> MessageResponse:
    """
    Desativar conta
    
    **Importante:**
    - Esta ação desativa a conta (soft delete)
    - O usuário não poderá mais fazer login
    - Os dados são mantidos por requisitos legais e LGPD
    - Para exclusão completa dos dados, entre em contato com o suporte
    
    **LGPD:**
    - Direito ao esquecimento: os dados serão anonimizados após o período de retenção legal
    - Logs de auditoria são mantidos por requisitos fiscais
    """
    await UsersService.delete_user_account(current_user, db)
    return MessageResponse(message="Conta desativada com sucesso")
