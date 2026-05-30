"""
Pipeline OCR → Classificação → TAX_EVENTS.
Orquestra todo o processamento documental.
"""
import re
from decimal import Decimal
from sqlalchemy.orm import Session
from app.shared.models import Document, DocumentStatus, OCRResult, OCRStatus, TaxEvent, TaxCategory, DocumentType
from .service import extract_text_from_bytes
from .classifier import classify_document, extract_metadata
from app.modules.storage.service import get_minio_client
from app.core.config import settings


def process_document(document_id: str, db: Session) -> bool:
    """
    Executa o pipeline completo para um documento:
    1. Download do storage
    2. OCR
    3. Classificação
    4. Criação de TAX_EVENTS
    """
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        return False

    ocr_result = db.query(OCRResult).filter(OCRResult.document_id == document_id).first()

    try:
        # 1. Atualizar status
        doc.status = DocumentStatus.PROCESSING
        db.commit()

        # 2. Download do arquivo
        content = _download_document(doc.storage_path)

        # 3. OCR
        ocr_output = extract_text_from_bytes(content, doc.mime_type)

        # Salvar resultado OCR
        if ocr_result:
            ocr_result.texto_extraido = ocr_output.texto
            ocr_result.confianca = ocr_output.confianca
            ocr_result.engine_utilizada = ocr_output.engine
            ocr_result.status = OCRStatus.DONE
        doc.status = DocumentStatus.OCR_DONE
        db.commit()

        # 4. Classificação
        doc_type = classify_document(ocr_output.texto)
        metadata = extract_metadata(ocr_output.texto)
        doc.tipo = doc_type
        if metadata.get("ano_base"):
            doc.ano_base = metadata["ano_base"]
        doc.status = DocumentStatus.CLASSIFIED
        db.commit()

        # 5. Criar TAX_EVENTS
        events_created = _create_tax_events(doc, ocr_output.texto, metadata, db)
        if events_created > 0:
            doc.status = DocumentStatus.TAX_EVENTS_CREATED

        db.commit()
        return True

    except Exception as e:
        if ocr_result:
            ocr_result.status = OCRStatus.ERROR
            ocr_result.erro_msg = str(e)[:500]
        doc.status = DocumentStatus.ERROR
        db.commit()
        return False


def _download_document(storage_path: str) -> bytes:
    client = get_minio_client()
    response = client.get_object(settings.MINIO_BUCKET_DOCUMENTS, storage_path)
    return response.read()


def _create_tax_events(doc: Document, text: str, metadata: dict, db: Session) -> int:
    """Cria TAX_EVENTS com base no tipo do documento e valores extraídos."""
    created = 0

    if doc.tipo == DocumentType.INFORME_RENDIMENTOS:
        created += _parse_informe_rendimentos(doc, text, metadata, db)
    elif doc.tipo == DocumentType.RECIBO_MEDICO:
        created += _parse_recibo_medico(doc, text, metadata, db)
    elif doc.tipo == DocumentType.DESPESA_EDUCACAO:
        created += _parse_despesa_educacao(doc, text, metadata, db)
    elif doc.tipo == DocumentType.DARF:
        created += _parse_darf(doc, text, metadata, db)

    return created


def _extract_values(text: str) -> list[Decimal]:
    """Extrai valores monetários do texto."""
    raw = re.findall(r"R\$\s*([\d\.]+,\d{2})", text)
    values = []
    for v in raw:
        try:
            normalized = v.replace(".", "").replace(",", ".")
            values.append(Decimal(normalized))
        except Exception:
            continue
    return values


def _parse_informe_rendimentos(doc: Document, text: str, meta: dict, db: Session) -> int:
    values = _extract_values(text)
    if not values:
        return 0

    created = 0
    text_lower = text.lower()

    # Rendimento tributável (maior valor geralmente)
    rend_match = re.search(r"rendimentos?\s+tributáveis[\s\S]{0,200}?R\$\s*([\d\.]+,\d{2})", text_lower)
    if rend_match:
        try:
            valor = Decimal(rend_match.group(1).replace(".", "").replace(",", "."))
            _add_event(doc, TaxCategory.RENDIMENTO_TRIBUTAVEL, valor, meta.get("fonte_pagadora", ""), meta.get("cnpj", ""), db)
            created += 1
        except Exception:
            pass

    # Retenção na fonte
    irrf_match = re.search(r"(?:irrf|imposto\s+retido)[\s\S]{0,200}?R\$\s*([\d\.]+,\d{2})", text_lower)
    if irrf_match:
        try:
            valor = Decimal(irrf_match.group(1).replace(".", "").replace(",", "."))
            _add_event(doc, TaxCategory.RETENCAO_FONTE, valor, meta.get("fonte_pagadora", ""), meta.get("cnpj", ""), db)
            created += 1
        except Exception:
            pass

    # Se nenhum padrão específico, usa os maiores valores como rendimento/retenção
    if created == 0 and len(values) >= 2:
        values_sorted = sorted(values, reverse=True)
        _add_event(doc, TaxCategory.RENDIMENTO_TRIBUTAVEL, values_sorted[0], "", "", db)
        _add_event(doc, TaxCategory.RETENCAO_FONTE, values_sorted[1], "", "", db)
        created = 2

    return created


def _parse_recibo_medico(doc: Document, text: str, meta: dict, db: Session) -> int:
    values = _extract_values(text)
    if not values:
        return 0
    _add_event(doc, TaxCategory.DEDUCAO_MEDICA, max(values), "", meta.get("cnpj", ""), db)
    return 1


def _parse_despesa_educacao(doc: Document, text: str, meta: dict, db: Session) -> int:
    values = _extract_values(text)
    if not values:
        return 0
    _add_event(doc, TaxCategory.DEDUCAO_EDUCACAO, max(values), "", meta.get("cnpj", ""), db)
    return 1


def _parse_darf(doc: Document, text: str, meta: dict, db: Session) -> int:
    values = _extract_values(text)
    if not values:
        return 0
    _add_event(doc, TaxCategory.RETENCAO_FONTE, max(values), "DARF", "", db)
    return 1


def _add_event(doc: Document, categoria: TaxCategory, valor: Decimal,
               fonte: str, cnpj: str, db: Session):
    event = TaxEvent(
        user_id=doc.user_id,
        document_id=doc.id,
        categoria=categoria,
        valor=valor,
        origem=doc.nome_original,
        fonte_pagadora=fonte or None,
        cnpj_fonte=cnpj or None,
        ano_base=doc.ano_base,
        metadata_json={"documento": doc.nome_original, "tipo": str(doc.tipo)},
    )
    db.add(event)
