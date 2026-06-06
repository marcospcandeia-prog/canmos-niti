"""
Documents Service
Business logic for document management
"""

from datetime import timedelta
from typing import BinaryIO, List, Optional

from fastapi import HTTPException, UploadFile, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.modules.documents.schemas import DocumentStats
from app.modules.storage.minio_service import get_minio_service
from app.shared.models.document import Document, OCRResult
from app.shared.models.user import User


# Allowed MIME types
ALLOWED_MIME_TYPES = [
    "application/pdf",
    "image/jpeg",
    "image/jpg",
    "image/png",
    "image/tiff",
    "image/bmp"
]

# Max file size: 10MB
MAX_FILE_SIZE = 10 * 1024 * 1024


class DocumentsService:
    """Documents service"""
    
    @staticmethod
    async def upload_document(
        file: UploadFile,
        user: User,
        db: AsyncSession
    ) -> Document:
        """
        Upload document to MinIO and create database record
        
        Args:
            file: Uploaded file
            user: Current authenticated user
            db: Database session
            
        Returns:
            Created document
            
        Raises:
            HTTPException: If validation fails or upload error
        """
        # Validate MIME type
        if file.content_type not in ALLOWED_MIME_TYPES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Tipo de arquivo não suportado. Tipos permitidos: {', '.join(ALLOWED_MIME_TYPES)}"
            )
        
        # Read file content
        file_content = await file.read()
        file_size = len(file_content)
        
        # Validate file size
        if file_size > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Arquivo muito grande. Tamanho máximo: {MAX_FILE_SIZE / 1024 / 1024}MB"
            )
        
        if file_size == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Arquivo vazio"
            )
        
        # Get MinIO service
        minio_service = get_minio_service()
        
        # Calculate file hash
        import io
        file_io = io.BytesIO(file_content)
        file_hash = minio_service.calculate_file_hash(file_io)
        
        # Check if file already uploaded by user (deduplication)
        stmt = select(Document).where(
            Document.user_id == user.id,
            Document.hash_arquivo == file_hash
        )
        result = await db.execute(stmt)
        existing_doc = result.scalar_one_or_none()
        
        if existing_doc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Este arquivo já foi enviado anteriormente"
            )
        
        # Generate storage path
        storage_path = minio_service.generate_storage_path(user.id, file.filename)
        
        # Upload to MinIO
        file_io.seek(0)  # Reset file pointer
        try:
            minio_service.upload_file(
                file_data=file_io,
                object_name=storage_path,
                content_type=file.content_type,
                file_size=file_size
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro ao fazer upload: {str(e)}"
            )
        
        # Create document record
        document = Document(
            user_id=user.id,
            nome_original=file.filename,
            storage_path=storage_path,
            mime_type=file.content_type,
            hash_arquivo=file_hash,
            status="uploaded"
        )
        
        db.add(document)
        await db.commit()
        await db.refresh(document)
        
        # TODO: Dispatch OCR task asynchronously
        # await dispatch_ocr_task(document.id)
        
        return document
    
    @staticmethod
    async def get_user_documents(
        user: User,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100
    ) -> List[Document]:
        """
        Get user's documents
        
        Args:
            user: Current authenticated user
            db: Database session
            skip: Offset for pagination
            limit: Limit for pagination
            
        Returns:
            List of documents
        """
        stmt = select(Document).where(
            Document.user_id == user.id
        ).order_by(
            Document.created_at.desc()
        ).offset(skip).limit(limit)
        
        result = await db.execute(stmt)
        documents = result.scalars().all()
        
        return list(documents)
    
    @staticmethod
    async def get_document_by_id(
        document_id: int,
        user: User,
        db: AsyncSession
    ) -> Optional[Document]:
        """
        Get document by ID (with ownership check)
        
        Args:
            document_id: Document ID
            user: Current authenticated user
            db: Database session
            
        Returns:
            Document if found and owned by user, None otherwise
        """
        stmt = select(Document).where(
            Document.id == document_id,
            Document.user_id == user.id
        ).options(
            selectinload(Document.ocr_result)
        )
        
        result = await db.execute(stmt)
        return result.scalar_one_or_none()
    
    @staticmethod
    async def delete_document(
        document_id: int,
        user: User,
        db: AsyncSession
    ) -> None:
        """
        Delete document (from MinIO and database)
        
        Args:
            document_id: Document ID
            user: Current authenticated user
            db: Database session
            
        Raises:
            HTTPException: If document not found or delete error
        """
        # Get document
        document = await DocumentsService.get_document_by_id(document_id, user, db)
        
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Documento não encontrado"
            )
        
        # Delete from MinIO
        minio_service = get_minio_service()
        try:
            minio_service.delete_file(document.storage_path)
        except Exception as e:
            # Log error but continue with database deletion
            print(f"Warning: Error deleting file from MinIO: {e}")
        
        # Delete from database (cascade will delete ocr_results and tax_events)
        await db.delete(document)
        await db.commit()
    
    @staticmethod
    async def get_download_url(
        document_id: int,
        user: User,
        db: AsyncSession,
        expires_hours: int = 1
    ) -> str:
        """
        Generate temporary download URL for document
        
        Args:
            document_id: Document ID
            user: Current authenticated user
            db: Database session
            expires_hours: URL expiration in hours
            
        Returns:
            Presigned download URL
            
        Raises:
            HTTPException: If document not found
        """
        # Get document
        document = await DocumentsService.get_document_by_id(document_id, user, db)
        
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Documento não encontrado"
            )
        
        # Generate presigned URL
        minio_service = get_minio_service()
        try:
            url = minio_service.get_presigned_url(
                object_name=document.storage_path,
                expires=timedelta(hours=expires_hours)
            )
            return url
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro ao gerar URL de download: {str(e)}"
            )
    
    @staticmethod
    async def get_document_stats(user: User, db: AsyncSession) -> DocumentStats:
        """
        Get document statistics for user
        
        Args:
            user: Current authenticated user
            db: Database session
            
        Returns:
            Document statistics
        """
        # Count total
        stmt = select(func.count(Document.id)).where(Document.user_id == user.id)
        result = await db.execute(stmt)
        total = result.scalar() or 0
        
        # Count by status
        stmt = select(func.count(Document.id)).where(
            Document.user_id == user.id,
            Document.status == "uploaded"
        )
        result = await db.execute(stmt)
        uploaded = result.scalar() or 0
        
        stmt = select(func.count(Document.id)).where(
            Document.user_id == user.id,
            Document.status == "processing"
        )
        result = await db.execute(stmt)
        processing = result.scalar() or 0
        
        stmt = select(func.count(Document.id)).where(
            Document.user_id == user.id,
            Document.status == "processed"
        )
        result = await db.execute(stmt)
        processed = result.scalar() or 0
        
        stmt = select(func.count(Document.id)).where(
            Document.user_id == user.id,
            Document.status == "error"
        )
        result = await db.execute(stmt)
        error = result.scalar() or 0
        
        # Count by type
        stmt = select(
            Document.tipo,
            func.count(Document.id)
        ).where(
            Document.user_id == user.id,
            Document.tipo.isnot(None)
        ).group_by(Document.tipo)
        
        result = await db.execute(stmt)
        by_type_rows = result.all()
        by_type = {row[0]: row[1] for row in by_type_rows}
        
        return DocumentStats(
            total=total,
            uploaded=uploaded,
            processing=processing,
            processed=processed,
            error=error,
            by_type=by_type
        )
