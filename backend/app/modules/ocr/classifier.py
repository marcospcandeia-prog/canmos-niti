"""
Classificador de documentos tributários.
Totalmente determinístico: regex + palavras-chave.
Sem IA — rastreável e auditável.
"""
import re
from app.shared.models import DocumentType


# Padrões de identificação por tipo
_PATTERNS = {
    DocumentType.INFORME_RENDIMENTOS: [
        r"informe\s+de\s+rendimentos",
        r"informes?\s+rendimento",
        r"comprovante\s+de\s+rendimentos",
        r"rendimentos\s+tributáveis",
        r"imposto\s+retido\s+na\s+fonte",
        r"irrf",
        r"declaração\s+de\s+rendimentos",
    ],
    DocumentType.RECIBO_MEDICO: [
        r"crm\s*[:\-]?\s*\d+",
        r"conselho\s+regional\s+de\s+medicina",
        r"consulta\s+médica",
        r"honorários\s+médicos",
        r"serviços\s+médicos",
        r"recibo\s+de\s+consulta",
        r"procedimento\s+cirúrgico",
        r"exame\s+laboratorial",
    ],
    DocumentType.DESPESA_EDUCACAO: [
        r"mensalidade\s+escolar",
        r"boleto\s+escolar",
        r"instituição\s+de\s+ensino",
        r"faculdade",
        r"universidade",
        r"colégio",
        r"escola",
        r"curso\s+técnico",
        r"matrícula",
        r"recibo\s+escolar",
    ],
    DocumentType.EXTRATO_BANCARIO: [
        r"extrato\s+bancário",
        r"extrato\s+de\s+conta",
        r"saldo\s+anterior",
        r"saldo\s+atual",
        r"lançamentos",
        r"débito\s+automático",
    ],
    DocumentType.EXTRATO_CORRETORA: [
        r"nota\s+de\s+corretagem",
        r"ações",
        r"fundos\s+de\s+investimento",
        r"dividendos",
        r"rendimentos\s+de\s+renda\s+variável",
        r"b3",
        r"bovespa",
        r"clear",
        r"xp\s+investimentos",
        r"rico",
        r"avenue",
    ],
    DocumentType.DARF: [
        r"darf",
        r"documento\s+de\s+arrecadação",
        r"receita\s+federal",
        r"período\s+de\s+apuração",
        r"código\s+da\s+receita",
    ],
}


def classify_document(text: str) -> DocumentType:
    """Retorna o tipo mais provável com base no texto extraído."""
    text_lower = text.lower()
    scores: dict[DocumentType, int] = {}

    for doc_type, patterns in _PATTERNS.items():
        score = sum(1 for p in patterns if re.search(p, text_lower))
        if score > 0:
            scores[doc_type] = score

    if not scores:
        return DocumentType.OUTROS

    return max(scores, key=lambda k: scores[k])


def extract_metadata(text: str) -> dict:
    """Extrai campos estruturados do texto OCR."""
    meta = {}

    # CPF
    cpf = re.search(r"\d{3}[\.\-]?\d{3}[\.\-]?\d{3}[\-\.]?\d{2}", text)
    if cpf:
        meta["cpf"] = re.sub(r"[^\d]", "", cpf.group())

    # CNPJ
    cnpj = re.search(r"\d{2}[\.\-]?\d{3}[\.\-]?\d{3}[\/\-]?\d{4}[\-\.]?\d{2}", text)
    if cnpj:
        meta["cnpj"] = re.sub(r"[^\d]", "", cnpj.group())

    # Valores monetários (R$ XXX.XXX,XX)
    valores = re.findall(r"R\$\s*[\d\.,]+", text)
    if valores:
        meta["valores_encontrados"] = valores[:10]

    # Ano base
    ano = re.search(r"\b(202[0-9]|201[5-9])\b", text)
    if ano:
        meta["ano_base"] = ano.group()

    # Nome da fonte pagadora
    fonte = re.search(r"(?:razão social|empresa|empregador)[:\s]+([A-Z][^\n]{3,60})", text, re.IGNORECASE)
    if fonte:
        meta["fonte_pagadora"] = fonte.group(1).strip()

    return meta
