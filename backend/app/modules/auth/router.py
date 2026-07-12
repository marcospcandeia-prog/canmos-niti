"""
Authentication Router
FastAPI endpoints for authentication
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config.settings import get_settings
from app.core.database.session import get_db
from app.modules.auth.schemas import (
    MessageResponse,
    Token,
    TokenRefresh,
    TokenResponse,
    UserLogin,
    UserRegister,
    UserResponse,
)
from app.modules.auth.service import AuthService

settings = get_settings()

router = APIRouter()


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar novo usuário",
    description="Cria uma nova conta de usuário no sistema",
    responses={
        201: {"description": "Usuário criado com sucesso"},
        400: {"description": "CPF ou email já cadastrado"},
    }
)
async def register(
    user_data: UserRegister,
    db: AsyncSession = Depends(get_db)
) -> UserResponse:
    """
    Registrar novo usuário
    
    - **nome**: Nome completo (mínimo 3 caracteres)
    - **cpf**: CPF com 11 dígitos (apenas números)
    - **email**: Email válido
    - **telefone**: Telefone (opcional)
    - **senha**: Senha com mínimo 8 caracteres
    - **lgpd_consent**: Consentimento LGPD (obrigatório)
    """
    return await AuthService.register_user(user_data, db)


@router.post(
    "/login",
    response_model=Token,
    summary="Fazer login",
    description="Autentica usuário e retorna tokens de acesso",
    responses={
        200: {"description": "Login realizado com sucesso"},
        401: {"description": "Credenciais inválidas"},
        403: {"description": "Usuário inativo"},
    }
)
async def login(
    credentials: UserLogin,
    db: AsyncSession = Depends(get_db)
) -> Token:
    """
    Fazer login
    
    - **email**: Email do usuário
    - **senha**: Senha do usuário
    
    Retorna:
    - **access_token**: Token de acesso (válido por 15 minutos)
    - **refresh_token**: Token de atualização (válido por 7 dias)
    """
    return await AuthService.login(credentials, db)


@router.post(
    "/refresh",
    response_model=TokenResponse,
    summary="Renovar access token",
    description="Gera novo access token usando refresh token",
    responses={
        200: {"description": "Token renovado com sucesso"},
        401: {"description": "Refresh token inválido ou expirado"},
    }
)
async def refresh_token(
    token_data: TokenRefresh,
    db: AsyncSession = Depends(get_db)
) -> TokenResponse:
    """
    Renovar access token
    
    - **refresh_token**: Refresh token válido
    
    Retorna:
    - **access_token**: Novo token de acesso
    """
    new_access_token = await AuthService.refresh_access_token(token_data.refresh_token, db)
    
    expires_in = settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    
    return TokenResponse(
        access_token=new_access_token,
        token_type="bearer",
        expires_in=expires_in
    )


@router.post(
    "/logout",
    response_model=MessageResponse,
    summary="Fazer logout",
    description="Invalida refresh token (implementação futura com blacklist)",
    responses={
        200: {"description": "Logout realizado com sucesso"},
    }
)
async def logout() -> MessageResponse:
    """
    Fazer logout
    
    **Nota**: Implementação atual apenas retorna mensagem de sucesso.
    Implementação futura incluirá blacklist de tokens no Redis.
    
    No frontend, remova os tokens do localStorage/cookies.
    """
    # TODO: Implementar blacklist de refresh tokens (Redis)
    # Por enquanto, o logout é responsabilidade do frontend (remover tokens)
    return MessageResponse(message="Logout realizado com sucesso")
