"""
Documents Router
FastAPI endpoints for document management
"""

from typing import List

from fastapi import APIRouter, BackgroundTasks, Depends, File, HTTPException, Query, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database.session import get_db
from app.core.middleware.auth import get_current_user
from app.modules.auth.schemas import MessageResponse
from app.modules.documents.schemas import (
    DocumentDownloadResponse,
    DocumentListResponse,
    DocumentResponse,
    DocumentStats,
    DocumentUploadResponse,
)
from app.modules.documents.service import DocumentsService
from app.shared.models.user import User

router = APIRouter()


@router.post(
    "/upload",
    response_model=DocumentUploadResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Fazer upload de documento",
    description="Faz upload de documento (PDF ou imagem) para processamento",
    responses={
        201: {"description": "Documento enviado com sucesso"},
        400: {"description": "Arquivo inválido ou já enviado"},
        401: {"description": "Não autenticado"},
    }
)
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(..., description="Arquivo para upload (PDF ou imagem)"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> DocumentUploadResponse:
    """
    Fazer upload de documento
    
    **Tipos suportados:**
    - PDF: application/pdf
    - Imagens: jpeg, jpg, png, tiff, bmp
    
    **Tamanho máximo:** 10MB
    
    **Processo:**
    1. Validação do arquivo
    2. Upload para MinIO
    3. Cálculo de hash SHA256 (deduplicação)
    4. Criação de registro no banco
    5. Disparo de OCR assíncrono automático
    """
    document = await DocumentsService.upload_document(file, current_user, db)

    from app.core.config.settings import get_settings
    _settings = get_settings()
    if _settings.APP_ENV != "test":
        from app.modules.ocr.service import process_document_background
        background_tasks.add_task(process_document_background, document.id)

    return DocumentUploadResponse.model_validate(document)


@router.get(
    "",
    response_model=List[DocumentListResponse],
    summary="Listar documentos do usuário",
    description="Lista todos os documentos do usuário autenticado",
    responses={
        200: {"description": "Lista retornada com sucesso"},
        401: {"description": "Não autenticado"},
    }
)
async def list_documents(
    skip: int = Query(0, ge=0, description="Offset para paginação"),
    limit: int = Query(100, ge=1, le=100, description="Limite de resultados"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> List[DocumentListResponse]:
    """
    Listar documentos do usuário
    
    **Paginação:**
    - `skip`: Número de registros para pular (padrão: 0)
    - `limit`: Máximo de registros (padrão: 100, máx: 100)
    
    **Ordenação:** Mais recentes primeiro (created_at DESC)
    """
    documents = await DocumentsService.get_user_documents(current_user, db, skip, limit)
    return [DocumentListResponse.model_validate(doc) for doc in documents]


@router.get(
    "/stats",
    response_model=DocumentStats,
    summary="Obter estatísticas de documentos",
    description="Retorna estatísticas de documentos do usuário",
    responses={
        200: {"description": "Estatísticas retornadas com sucesso"},
        401: {"description": "Não autenticado"},
    }
)
async def get_documents_stats(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> DocumentStats:
    """
    Obter estatísticas de documentos
    
    Retorna:
    - Total de documentos
    - Contagem por status (uploaded, processing, processed, error)
    - Contagem por tipo de documento
    """
    return await DocumentsService.get_document_stats(current_user, db)


@router.get(
    "/{document_id}",
    response_model=DocumentResponse,
    summary="Obter detalhes do documento",
    description="Retorna detalhes completos de um documento, incluindo resultado OCR se disponível",
    responses={
        200: {"description": "Documento retornado com sucesso"},
        401: {"description": "Não autenticado"},
        404: {"description": "Documento não encontrado"},
    }
)
async def get_document(
    document_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> DocumentResponse:
    """
    Obter detalhes do documento
    
    Retorna:
    - Metadados do documento
    - Resultado OCR (se disponível)
    - Status do processamento
    """
    document = await DocumentsService.get_document_by_id(document_id, current_user, db)
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Documento não encontrado"
        )
    
    # Build response with OCR data if exists
    response_data = {
        "id": document.id,
        "user_id": document.user_id,
        "tipo": document.tipo,
        "nome_original": document.nome_original,
        "storage_path": document.storage_path,
        "mime_type": document.mime_type,
        "hash_arquivo": document.hash_arquivo,
        "status": document.status,
        "created_at": document.created_at,
        "updated_at": document.updated_at,
    }
    
    if document.ocr_result:
        response_data.update({
            "ocr_texto": document.ocr_result.texto_extraido,
            "ocr_confianca": document.ocr_result.confianca,
            "ocr_engine": document.ocr_result.engine_utilizada,
            "ocr_status": document.ocr_result.status,
        })
    
    return DocumentResponse(**response_data)


@router.get(
    "/{document_id}/download",
    response_model=DocumentDownloadResponse,
    summary="Obter URL de download do documento",
    description="Gera URL temporária para download do documento",
    responses={
        200: {"description": "URL gerada com sucesso"},
        401: {"description": "Não autenticado"},
        404: {"description": "Documento não encontrado"},
    }
)
async def download_document(
    document_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> DocumentDownloadResponse:
    """
    Obter URL de download do documento
    
    Gera uma URL temporária (presigned) para download direto do MinIO.
    
    **Validade:** 1 hora
    
    **Nota:** A URL permite download direto sem autenticação adicional,
    mas expira após 1 hora.
    """
    url = await DocumentsService.get_download_url(document_id, current_user, db)
    
    return DocumentDownloadResponse(
        download_url=url,
        expires_in=3600  # 1 hour
    )


@router.delete(
    "/{document_id}",
    response_model=MessageResponse,
    summary="Excluir documento",
    description="Exclui documento do MinIO e banco de dados",
    responses={
        200: {"description": "Documento excluído com sucesso"},
        401: {"description": "Não autenticado"},
        404: {"description": "Documento não encontrado"},
    }
)
async def delete_document(
    document_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> MessageResponse:
    """
    Excluir documento
    
    **Atenção:** Esta ação é irreversível!
    
    - Remove arquivo do MinIO
    - Remove registro do banco de dados
    - Remove resultados OCR associados (cascade)
    - Remove eventos tributários vinculados (cascade)
    """
    await DocumentsService.delete_document(document_id, current_user, db)
    return MessageResponse(message="Documento excluído com sucesso")
