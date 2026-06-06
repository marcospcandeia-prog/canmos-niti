"""
Users Service
Business logic for user profile management
"""

from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.security.password import hash_password, verify_password
from app.modules.users.schemas import PasswordChange, UserProfileUpdate, UserStats
from app.shared.models.audit import AuditLog
from app.shared.models.tax import Declaration
from app.shared.models.document import Document
from app.shared.models.tax import TaxEvent
from app.shared.models.user import User, UserProfile


class UsersService:
    """Users service"""
    
    @staticmethod
    async def get_user_profile(user: User, db: AsyncSession) -> dict:
        """
        Get user profile with extended information
        
        Args:
            user: Current authenticated user
            db: Database session
            
        Returns:
            User profile with all fields including profile data
        """
        # Load user with profile relationship
        stmt = select(User).where(User.id == user.id).options(
            selectinload(User.profile)
        )
        result = await db.execute(stmt)
        user_with_profile = result.scalar_one()
        
        # Build response with user + profile data
        profile_data = {
            "id": user_with_profile.id,
            "uuid": user_with_profile.uuid,
            "nome": user_with_profile.nome,
            "cpf": user_with_profile.cpf,
            "email": user_with_profile.email,
            "telefone": user_with_profile.telefone,
            "status": user_with_profile.status,
            "lgpd_consent_at": user_with_profile.lgpd_consent_at,
            "created_at": user_with_profile.created_at,
            "updated_at": user_with_profile.updated_at,
        }
        
        # Add profile fields if exists
        if user_with_profile.profile:
            profile_data.update({
                "profissao": user_with_profile.profile.profissao,
                "estado_civil": user_with_profile.profile.estado_civil,
                "possui_dependentes": user_with_profile.profile.possui_dependentes,
                "possui_investimentos": user_with_profile.profile.possui_investimentos,
            })
        else:
            # Default values if profile doesn't exist
            profile_data.update({
                "profissao": None,
                "estado_civil": None,
                "possui_dependentes": False,
                "possui_investimentos": False,
            })
        
        return profile_data
    
    @staticmethod
    async def update_user_profile(
        user: User,
        update_data: UserProfileUpdate,
        db: AsyncSession
    ) -> dict:
        """
        Update user profile
        
        Args:
            user: Current authenticated user
            update_data: Profile update data
            db: Database session
            
        Returns:
            Updated user profile
        """
        # Load user with profile
        stmt = select(User).where(User.id == user.id).options(
            selectinload(User.profile)
        )
        result = await db.execute(stmt)
        user_obj = result.scalar_one()
        
        # Update user fields
        if update_data.nome is not None:
            user_obj.nome = update_data.nome
        
        if update_data.telefone is not None:
            user_obj.telefone = update_data.telefone
        
        # Update or create profile
        if user_obj.profile:
            profile = user_obj.profile
        else:
            # Create profile if doesn't exist
            profile = UserProfile(user_id=user_obj.id)
            db.add(profile)
        
        # Update profile fields
        if update_data.profissao is not None:
            profile.profissao = update_data.profissao
        
        if update_data.estado_civil is not None:
            profile.estado_civil = update_data.estado_civil
        
        if update_data.possui_dependentes is not None:
            profile.possui_dependentes = update_data.possui_dependentes
        
        if update_data.possui_investimentos is not None:
            profile.possui_investimentos = update_data.possui_investimentos
        
        await db.commit()
        await db.refresh(user_obj)
        
        # Return updated profile
        return await UsersService.get_user_profile(user_obj, db)
    
    @staticmethod
    async def change_password(
        user: User,
        password_data: PasswordChange,
        db: AsyncSession
    ) -> None:
        """
        Change user password
        
        Args:
            user: Current authenticated user
            password_data: Password change data
            db: Database session
            
        Raises:
            HTTPException: If current password is incorrect
        """
        # Verify current password
        if not verify_password(password_data.senha_atual, user.senha_hash):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Senha atual incorreta"
            )
        
        # Hash new password
        new_password_hash = hash_password(password_data.senha_nova)
        
        # Update password
        user.senha_hash = new_password_hash
        await db.commit()
    
    @staticmethod
    async def get_user_stats(user: User, db: AsyncSession) -> UserStats:
        """
        Get user statistics
        
        Args:
            user: Current authenticated user
            db: Database session
            
        Returns:
            User statistics
        """
        # Count documents
        stmt = select(func.count(Document.id)).where(Document.user_id == user.id)
        result = await db.execute(stmt)
        total_documents = result.scalar() or 0
        
        # Count processed documents
        stmt = select(func.count(Document.id)).where(
            Document.user_id == user.id,
            Document.status == "processed"
        )
        result = await db.execute(stmt)
        documents_processed = result.scalar() or 0
        
        # Count tax events
        stmt = select(func.count(TaxEvent.id)).where(TaxEvent.user_id == user.id)
        result = await db.execute(stmt)
        total_tax_events = result.scalar() or 0
        
        # Count declarations
        stmt = select(func.count(Declaration.id)).where(Declaration.user_id == user.id)
        result = await db.execute(stmt)
        declarations_count = result.scalar() or 0
        
        # Get last activity (most recent audit log)
        stmt = select(AuditLog.created_at).where(
            AuditLog.user_id == user.id
        ).order_by(AuditLog.created_at.desc()).limit(1)
        result = await db.execute(stmt)
        last_activity = result.scalar_one_or_none()
        
        return UserStats(
            total_documents=total_documents,
            documents_processed=documents_processed,
            total_tax_events=total_tax_events,
            declarations_count=declarations_count,
            last_activity=last_activity
        )
    
    @staticmethod
    async def delete_user_account(user: User, db: AsyncSession) -> None:
        """
        Delete user account (soft delete - set status to inactive)
        
        Args:
            user: Current authenticated user
            db: Database session
            
        Note:
            This is a soft delete. Hard delete with LGPD compliance
            should be implemented separately with proper data anonymization.
        """
        user.status = "inactive"
        await db.commit()
        
        # TODO: Implement full LGPD compliance:
        # - Schedule hard delete after retention period
        # - Anonymize personal data
        # - Keep audit logs for legal requirements
