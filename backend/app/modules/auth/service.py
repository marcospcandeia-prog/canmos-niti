"""
Authentication Service
Business logic for user authentication
"""

from datetime import datetime
from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security.jwt import create_access_token, create_refresh_token, decode_token, verify_token_type
from app.core.security.password import hash_password, verify_password
from app.modules.auth.schemas import Token, UserLogin, UserRegister, UserResponse
from app.shared.models.user import User, UserProfile


class AuthService:
    """Authentication service"""
    
    @staticmethod
    async def register_user(
        user_data: UserRegister,
        db: AsyncSession
    ) -> UserResponse:
        """
        Register new user
        
        Args:
            user_data: User registration data
            db: Database session
            
        Returns:
            Created user data
            
        Raises:
            HTTPException: If CPF or email already exists
        """
        # Check if CPF already exists
        stmt = select(User).where(User.cpf == user_data.cpf)
        result = await db.execute(stmt)
        existing_user = result.scalar_one_or_none()
        
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="CPF já cadastrado"
            )
        
        # Check if email already exists
        stmt = select(User).where(User.email == user_data.email)
        result = await db.execute(stmt)
        existing_user = result.scalar_one_or_none()
        
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email já cadastrado"
            )
        
        # Hash password
        hashed_password = hash_password(user_data.senha)
        
        # Create user
        new_user = User(
            nome=user_data.nome,
            cpf=user_data.cpf,
            email=user_data.email,
            telefone=user_data.telefone,
            senha_hash=hashed_password,
            status="active",
            lgpd_consent_at=datetime.utcnow() if user_data.lgpd_consent else None
        )
        
        db.add(new_user)
        await db.flush()  # Get user.id without committing
        
        # Create user profile
        user_profile = UserProfile(
            user_id=new_user.id,
            possui_dependentes=False,
            possui_investimentos=False
        )
        
        db.add(user_profile)
        await db.commit()
        await db.refresh(new_user)
        
        return UserResponse.model_validate(new_user)
    
    @staticmethod
    async def authenticate_user(
        credentials: UserLogin,
        db: AsyncSession
    ) -> User:
        """
        Authenticate user with email and password
        
        Args:
            credentials: Login credentials
            db: Database session
            
        Returns:
            Authenticated user
            
        Raises:
            HTTPException: If credentials are invalid
        """
        # Find user by email
        stmt = select(User).where(User.email == credentials.email)
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Email ou senha incorretos",
                headers={"WWW-Authenticate": "Bearer"}
            )
        
        # Verify password
        if not verify_password(credentials.senha, user.senha_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Email ou senha incorretos",
                headers={"WWW-Authenticate": "Bearer"}
            )
        
        # Check if user is active
        if user.status != "active":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Usuário inativo"
            )
        
        return user
    
    @staticmethod
    async def login(
        credentials: UserLogin,
        db: AsyncSession
    ) -> Token:
        """
        Login user and return tokens
        
        Args:
            credentials: Login credentials
            db: Database session
            
        Returns:
            Access and refresh tokens
        """
        # Authenticate user
        user = await AuthService.authenticate_user(credentials, db)
        
        # Create tokens
        access_token = create_access_token(data={"sub": user.email, "user_id": user.id})
        refresh_token = create_refresh_token(data={"sub": user.email, "user_id": user.id})
        
        # Get expiration time from settings
        from app.core.config.settings import get_settings
        settings = get_settings()
        expires_in = settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60  # Convert to seconds
        
        return Token(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=expires_in
        )
    
    @staticmethod
    async def refresh_access_token(refresh_token: str, db: AsyncSession) -> str:
        """
        Refresh access token using refresh token
        
        Args:
            refresh_token: Refresh token
            db: Database session
            
        Returns:
            New access token
            
        Raises:
            HTTPException: If refresh token is invalid
        """
        try:
            # Decode refresh token
            payload = decode_token(refresh_token)
            
            # Verify token type
            if not verify_token_type(payload, "refresh"):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token inválido",
                    headers={"WWW-Authenticate": "Bearer"}
                )
            
            # Get user email from token
            email = payload.get("sub")
            if not email:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token inválido",
                    headers={"WWW-Authenticate": "Bearer"}
                )
            
            # Verify user exists
            stmt = select(User).where(User.email == email)
            result = await db.execute(stmt)
            user = result.scalar_one_or_none()
            
            if not user or user.status != "active":
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Usuário não encontrado ou inativo",
                    headers={"WWW-Authenticate": "Bearer"}
                )
            
            # Create new access token
            new_access_token = create_access_token(
                data={"sub": user.email, "user_id": user.id}
            )
            
            return new_access_token
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Token inválido: {str(e)}",
                headers={"WWW-Authenticate": "Bearer"}
            )
    
    @staticmethod
    async def get_user_by_email(email: str, db: AsyncSession) -> Optional[User]:
        """
        Get user by email
        
        Args:
            email: User email
            db: Database session
            
        Returns:
            User if found, None otherwise
        """
        stmt = select(User).where(User.email == email)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()
