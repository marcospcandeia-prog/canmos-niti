"""Testes do classificador OCR — determinístico."""
from app.modules.ocr.classifier import classify_document, extract_metadata
from app.shared.models import DocumentType


def test_classifica_informe_rendimentos():
    texto = "INFORME DE RENDIMENTOS TRIBUTÁVEIS\nEmpresa XYZ LTDA\nIRRF: R$ 1.200,00"
    assert classify_document(texto) == DocumentType.INFORME_RENDIMENTOS


def test_classifica_recibo_medico():
    texto = "Recibo de Consulta Médica\nCRM: 12345-SP\nHonorários médicos: R$ 250,00"
    assert classify_document(texto) == DocumentType.RECIBO_MEDICO


def test_classifica_despesa_educacao():
    texto = "Mensalidade Escolar\nInstituição de Ensino Superior ABC\nMatrícula 2024"
    assert classify_document(texto) == DocumentType.DESPESA_EDUCACAO


def test_classifica_darf():
    texto = "DARF - Documento de Arrecadação de Receitas Federais\nCódigo da Receita: 0190"
    assert classify_document(texto) == DocumentType.DARF


def test_desconhecido_retorna_outros():
    texto = "Lorem ipsum dolor sit amet consectetur adipiscing"
    assert classify_document(texto) == DocumentType.OUTROS


def test_extrai_cpf():
    texto = "CPF do contribuinte: 123.456.789-09"
    meta = extract_metadata(texto)
    assert meta.get("cpf") == "12345678909"


def test_extrai_cnpj():
    texto = "CNPJ: 12.345.678/0001-90"
    meta = extract_metadata(texto)
    assert meta.get("cnpj") == "12345678000190"


def test_extrai_ano_base():
    texto = "Ano-base: 2024 — Declaração IRPF"
    meta = extract_metadata(texto)
    assert meta.get("ano_base") == "2024"


def test_extrai_valores():
    texto = "Rendimento: R$ 5.000,00 e R$ 1.200,50"
    meta = extract_metadata(texto)
    assert len(meta.get("valores_encontrados", [])) >= 2
