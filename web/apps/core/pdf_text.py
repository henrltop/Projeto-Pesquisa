"""Extracao de texto da camada OCR dos PDFs do IOMAT (sem Tesseract).

Os PDFs de pagina do IOMAT ja trazem uma camada de texto (OCR feito pela
propria fonte). Usamos pdfplumber para ler esse texto, o que nos permite
montar o contexto de paginas vizinhas sem depender da busca por termo.
"""
from __future__ import annotations

import logging
import tempfile
from pathlib import Path

from .iomat_client import baixar_pdf

logger = logging.getLogger(__name__)

# pdfminer (usado pelo pdfplumber) e bem verboso; silencia o ruido.
logging.getLogger("pdfminer").setLevel(logging.ERROR)
logging.getLogger("pdfplumber").setLevel(logging.ERROR)


def extrair_texto_pdf(caminho: str | Path) -> str:
    """Extrai todo o texto de um PDF local. Retorna '' se nao for possivel."""
    try:
        import pdfplumber
    except ImportError:
        logger.error("pdfplumber nao instalado; nao da pra extrair texto de PDF.")
        return ""
    try:
        partes: list[str] = []
        with pdfplumber.open(str(caminho)) as pdf:
            for pagina in pdf.pages:
                partes.append(pagina.extract_text() or "")
        return "\n".join(partes).strip()
    except Exception:  # noqa: BLE001
        logger.exception("Falha ao extrair texto do PDF %s", caminho)
        return ""


def texto_da_pagina(tipo_edicao: int, edicao_id: str, pagina: int) -> str | None:
    """Baixa o PDF de uma pagina arbitraria e devolve o texto OCR.

    Retorna None se a pagina nao existir ou o download falhar.
    O PDF e baixado para um arquivo temporario e removido em seguida.
    """
    if pagina < 1:
        return None
    tmp = None
    try:
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as fh:
            tmp = fh.name
        ok = baixar_pdf(tipo_edicao, edicao_id, pagina, tmp)
        if not ok:
            return None
        return extrair_texto_pdf(tmp)
    except Exception:  # noqa: BLE001
        logger.exception("Erro ao obter texto da pagina %s/%s", edicao_id, pagina)
        return None
    finally:
        if tmp:
            try:
                Path(tmp).unlink(missing_ok=True)
            except OSError:
                pass
