from typing import Optional

from sqlalchemy.orm import Session

from app.core.utils import generate_hash
from app.modules.storage.service import StorageService
from app.shared.models.document import Document, DocumentStatus, DocumentType, OcrResult, TaxEvent


class DocumentService:
    def __init__(self, db: Session):
        self.db = db
        self.storage = StorageService()

    async def upload(self, user_id: str, file_content: bytes, filename: str, mime_type: str, tipo: str = "outro"):
        file_hash = generate_hash(file_content)
        storage_path = await self.storage.upload(user_id, filename, file_content, mime_type)

        doc = Document(
            user_id=user_id,
            tipo=DocumentType(tipo) if tipo else DocumentType.OUTRO,
            nome_original=filename,
            storage_path=storage_path,
            mime_type=mime_type,
            hash_arquivo=file_hash,
            tamanho_bytes=str(len(file_content)),
            status=DocumentStatus.PENDING,
        )
        self.db.add(doc)
        self.db.commit()
        self.db.refresh(doc)
        return doc

    def list_by_user(self, user_id: str, skip: int = 0, limit: int = 20):
        return (
            self.db.query(Document)
            .filter(Document.user_id == user_id)
            .order_by(Document.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_id(self, doc_id: str, user_id: str) -> Optional[Document]:
        return (
            self.db.query(Document)
            .filter(Document.id == doc_id, Document.user_id == user_id)
            .first()
        )

    def count_by_user(self, user_id: str) -> int:
        return self.db.query(Document).filter(Document.user_id == user_id).count()

    def delete(self, doc_id: str, user_id: str) -> bool:
        doc = self.get_by_id(doc_id, user_id)
        if not doc:
            return False

        self.db.query(TaxEvent).filter(TaxEvent.document_id == doc.id).delete()
        self.db.query(OcrResult).filter(OcrResult.document_id == doc.id).delete()

        from app.modules.storage.service import StorageService
        import asyncio
        try:
            asyncio.run(StorageService().delete(doc.storage_path))
        except Exception:
            pass

        self.db.delete(doc)
        self.db.commit()
        return True

    def count_by_status(self, user_id: str) -> dict:
        result = {}
        for status in DocumentStatus:
            count = (
                self.db.query(Document)
                .filter(Document.user_id == user_id, Document.status == status)
                .count()
            )
            if count > 0:
                result[status.value] = count
        return result
