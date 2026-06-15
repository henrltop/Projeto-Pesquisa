"""Monta a janela de contexto de um documento (pagina) expandindo para as
paginas vizinhas da mesma edicao ate encontrar o inicio e o fim do ato.

Motivacao: um ato normativo (lei, decreto, resolucao) frequentemente comeca
numa pagina e termina em outra. Classificar apenas a pagina que casou com o
termo perde contexto. Aqui expandimos para tras e para frente, com deteccao
heuristica de fronteira e um teto de seguranca.
"""
from __future__ import annotations

import logging
import re

import requests

from .delimitador import Delimitador
from .iomat_client import DEFAULT_HEADERS
from .pdf_text import texto_da_pagina

logger = logging.getLogger(__name__)

BASE_EDICAO = "https://api.iomat.mt.gov.br/transparencia/v1/diarios"

# Cabecalho de ato: palavra-chave seguida de numero/data por perto.
# Tolerante a ruido de OCR (N0, Nº, N., etc.).
_HEADER = re.compile(
    r"(?i)\b(LEI(\s+COMPLEMENTAR)?|DECRETO([\s-]*LEI)?|RESOLU\w*|PORTARIA|"
    r"INSTRU\w+\s+NORMATIVA|EMENDA\s+CONSTITUCIONAL|MEDIDA\s+PROVIS\w*|"
    r"DECRETO\s+LEGISLATIVO|REGIMENTO|ESTATUTO|EDITAL|DIRETRIZ\w*|PLANO)"
    r"\s*(N[º°o0\.\s]*\d|DE\s+\d)"
)

# Fechamento de ato: clausula de vigencia ou bloco de assinatura.
_CLOSING = re.compile(
    r"(?i)(entra\s+em\s+vigor|revogam[\s-]*se\s+as\s+disposi|pal[aá]cio|"
    r"paiagu|governador\s+do\s+estado|secret[aá]rio\s+de\s+estado)"
)

CHARS_POR_PAGINA = 6000     # corte por pagina ao montar o texto final
CHARS_TOTAL_MAX = 30000     # teto do texto montado enviado a IA


def numpag_edicao(tipo_edicao: int, edicao_id: str) -> int | None:
    """Retorna o numero total de paginas da edicao, ou None se nao descobrir."""
    url = f"{BASE_EDICAO}/{tipo_edicao}/edicoes/{edicao_id}"
    try:
        r = requests.get(url, headers=DEFAULT_HEADERS, timeout=20)
        r.raise_for_status()
        data = r.json()
        n = data.get("numpag")
        return int(n) if n else None
    except Exception:  # noqa: BLE001
        logger.warning("Nao foi possivel obter numpag da edicao %s", edicao_id)
        return None


def _comeca_com_cabecalho(texto: str, janela: int = 300) -> bool:
    return bool(_HEADER.search(texto[:janela]))


def _tem_fechamento(texto: str, janela: int = 900) -> bool:
    return bool(_CLOSING.search(texto[-janela:]))


def montar_contexto(
    *,
    tipo_edicao: int,
    edicao_id: str,
    pagina: int,
    texto_alvo: str,
    cap: int = 5,
    cache: dict | None = None,
) -> dict:
    """Monta o contexto expandindo paginas vizinhas ate as fronteiras do ato.

    Retorna dict com:
      - texto: str montado (com marcadores de pagina; pagina-alvo destacada)
      - paginas: list[int] incluidas, em ordem
      - expandiu_tras / expandiu_frente: int (quantas paginas extras de cada lado)
      - total_edicao: int | None
    """
    cache = cache if cache is not None else {}
    texto_alvo = texto_alvo or ""

    def page_text(p: int) -> str | None:
        chave = (tipo_edicao, edicao_id, p)
        if chave not in cache:
            cache[chave] = texto_da_pagina(tipo_edicao, edicao_id, p)
        return cache[chave]

    total = numpag_edicao(tipo_edicao, edicao_id)

    paginas: dict[int, str] = {pagina: texto_alvo}

    # ---- expansao para tras (achar inicio do ato) ----
    expandiu_tras = 0
    if not _comeca_com_cabecalho(texto_alvo):
        for passo in range(cap):
            p = pagina - passo - 1
            if p < 1:
                break
            txt = page_text(p)
            if not txt:
                break
            paginas[p] = txt
            expandiu_tras += 1
            if _HEADER.search(txt):  # achou um inicio de ato; para aqui
                break

    # ---- expansao para frente (achar fim do ato) ----
    expandiu_frente = 0
    if not _tem_fechamento(texto_alvo):
        for passo in range(cap):
            p = pagina + passo + 1
            if total and p > total:
                break
            txt = page_text(p)
            if not txt:
                break
            # Se a proxima pagina ja COMECA com um novo ato, o nosso terminou antes.
            if _comeca_com_cabecalho(txt, janela=200):
                break
            paginas[p] = txt
            expandiu_frente += 1
            if _tem_fechamento(txt):  # ato terminou nesta pagina
                break

    # ---- montagem do texto final ----
    ordenadas = sorted(paginas.keys())
    blocos: list[str] = []
    for p in ordenadas:
        corpo = (paginas[p] or "")[:CHARS_POR_PAGINA]
        if p == pagina:
            blocos.append(
                f"===== PAGINA {p} (PAGINA-ALVO — classifique o ato desta pagina) =====\n{corpo}"
            )
        else:
            rotulo = "anterior" if p < pagina else "seguinte"
            blocos.append(f"----- PAGINA {p} (contexto {rotulo}) -----\n{corpo}")
    texto = "\n\n".join(blocos)[:CHARS_TOTAL_MAX]

    return {
        "texto": texto,
        "paginas": ordenadas,
        "expandiu_tras": expandiu_tras,
        "expandiu_frente": expandiu_frente,
        "total_edicao": total,
    }


# Quantas paginas vizinhas oferecer ao delimitador (para cada lado).
JANELA_DELIMITADOR = 2


def montar_contexto_delimitado(
    *,
    tipo_edicao: int,
    edicao_id: str,
    pagina: int,
    texto_alvo: str,
    delimitador: Delimitador,
    janela: int = JANELA_DELIMITADOR,
    cache: dict | None = None,
) -> dict:
    """Monta o contexto usando o LLM local (gpt-oss) para delimitar o ato.

    Fluxo (Variante B):
      1. Reune a pagina-alvo + ate `janela` vizinhas de cada lado (texto OCR).
      2. Pede ao delimitador quais paginas formam o MESMO ato (so numeros).
      3. Recorta o texto OCR ORIGINAL dessas paginas (fiel, sem reescrita).

    Fallback: se o delimitador falhar/nao responder, usa a pagina-alvo isolada
    (configuracao de maior concordancia com o humano).

    Retorna o mesmo formato de montar_contexto, com chaves extras:
      - via_delimitador: bool
      - paginas_oferecidas: list[int]
    """
    cache = cache if cache is not None else {}
    texto_alvo = texto_alvo or ""

    def page_text(p: int) -> str | None:
        if p == pagina:
            return texto_alvo
        chave = (tipo_edicao, edicao_id, p)
        if chave not in cache:
            cache[chave] = texto_da_pagina(tipo_edicao, edicao_id, p)
        return cache[chave]

    total = numpag_edicao(tipo_edicao, edicao_id)

    # 1. junta paginas oferecidas (alvo + vizinhas que existirem)
    oferecidas: dict[int, str] = {}
    for p in range(pagina - janela, pagina + janela + 1):
        if p < 1:
            continue
        if total and p > total:
            continue
        txt = page_text(p)
        if txt:
            oferecidas[p] = txt

    # 2. delimita
    via_delim = False
    escolhidas = None
    if delimitador and delimitador.configurado and len(oferecidas) > 1:
        try:
            escolhidas = delimitador.delimitar(pagina, oferecidas)
            via_delim = bool(escolhidas)
        except Exception:  # noqa: BLE001
            logger.exception("Falha no delimitador; usando fallback de pagina isolada")
            escolhidas = None

    # 3. fallback: pagina-alvo isolada
    if not escolhidas:
        escolhidas = [pagina]

    # garante contiguidade: o ato e um bloco continuo, sem buracos
    escolhidas = sorted(set(escolhidas))
    escolhidas = list(range(min(escolhidas), max(escolhidas) + 1))

    # 4. monta texto fiel das paginas escolhidas
    blocos: list[str] = []
    for p in escolhidas:
        corpo = (oferecidas.get(p) or page_text(p) or "")[:CHARS_POR_PAGINA]
        if p == pagina:
            blocos.append(
                f"===== PAGINA {p} (PAGINA-ALVO — classifique o ato desta pagina) =====\n{corpo}"
            )
        else:
            rotulo = "anterior" if p < pagina else "seguinte"
            blocos.append(f"----- PAGINA {p} (contexto {rotulo}) -----\n{corpo}")
    texto = "\n\n".join(blocos)[:CHARS_TOTAL_MAX]

    return {
        "texto": texto,
        "paginas": escolhidas,
        "via_delimitador": via_delim,
        "paginas_oferecidas": sorted(oferecidas.keys()),
        "total_edicao": total,
    }
