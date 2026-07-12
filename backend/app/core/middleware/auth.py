"""
Authentication Middleware
Dependency for protected routes
"""

from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database.session import get_db
from app.core.security.jwt import decode_token, verify_token_type
from app.modules.auth.service import AuthService
from app.shared.models.user import User

# HTTP Bearer security scheme.
# auto_error=False so that a missing Authorization header yields our own
# 401 response instead of FastAPI's default 403, keeping missing and invalid
# credentials consistent (both -> 401 Unauthorized).
security = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> User:
    """
    Dependency to get current authenticated user from JWT token
    
    Args:
        credentials: HTTP Bearer token from Authorization header
        db: Database session
        
    Returns:
        Current authenticated user
        
    Raises:
        HTTPException: If token is invalid or user not found
        
    Usage:
        @app.get("/protected")
        async def protected_route(current_user: User = Depends(get_current_user)):
            return {"user": current_user.email}
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Não foi possível validar as credenciais",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # No Authorization header provided
    if credentials is None:
        raise credentials_exception

    try:
        # Get token from credentials
        token = credentials.credentials
        
        # Decode token
        payload = decode_token(token)
        
        # Verify token type is access
        if not verify_token_type(payload, "access"):
            raise credentials_exception
        
        # Get user email from token
        email: Optional[str] = payload.get("sub")
        if email is None:
            raise credentials_exception
        
    except JWTError:
        raise credentials_exception
    
    # Get user from database
    user = await AuthService.get_user_by_email(email, db)
    
    if user is None:
        raise credentials_exception
    
    # Check if user is active
    if user.status != "active":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuário inativo"
        )
    
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Dependency to get current active user
    (additional layer of validation)
    
    Args:
        current_user: User from get_current_user dependency
        
    Returns:
        Current active user
        
    Raises:
        HTTPException: If user is not active
    """
    if current_user.status != "active":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuário inativo"
        )
    return current_user


def get_optional_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False)),
    db: AsyncSession = Depends(get_db)
) -> Optional[User]:
    """
    Dependency to get current user if token is provided (optional)
    Useful for routes that work with or without authentication
    
    Args:
        credentials: Optional HTTP Bearer token
        db: Database session
        
    Returns:
        Current user if authenticated, None otherwise
        
    Usage:
        @app.get("/public")
        async def public_route(user: Optional[User] = Depends(get_optional_current_user)):
            if user:
                return {"message": f"Hello {user.nome}"}
            return {"message": "Hello guest"}
    """
    if credentials is None:
        return None
    
    try:
        token = credentials.credentials
        payload = decode_token(token)
        
        if not verify_token_type(payload, "access"):
            return None
        
        email = payload.get("sub")
        if email is None:
            return None
        
        # Get user from database (async)
        import asyncio
        user = asyncio.create_task(AuthService.get_user_by_email(email, db))
        return asyncio.run(user)
        
    except Exception:
        return None
