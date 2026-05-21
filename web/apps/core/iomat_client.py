"""Cliente HTTP para a API publica do IOMAT (transparencia). Esqueleto para Fase B."""
from __future__ import annotations

import time
import urllib.parse
from dataclasses import dataclass
from typing import Iterable, Iterator

import requests

BASE_BUSCA = "https://api.iomat.mt.gov.br/busca/v1/buscas"
BASE_PDF = "https://api.iomat.mt.gov.br/transparencia/v1/diarios"

DEFAULT_HEADERS = {
    "accept": "application/json",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Connection": "keep-alive",
}


class IomatError(Exception):
    pass


@dataclass
class Hit:
    edicao_id: str
    tipo_edicao: int
    pagina: int
    ano: int
    data_pub: str
    nome_edicao: str
    texto_bruto: str
    link: str


def _request_json(url: str, params: dict, retries: int = 3, timeout: int = 20) -> dict:
    for tentativa in range(retries):
        try:
            res = requests.get(url, params=params, headers=DEFAULT_HEADERS, timeout=timeout)
            res.raise_for_status()
            return res.json()
        except requests.exceptions.ConnectionError:
            if tentativa < retries - 1:
                time.sleep(5)
                continue
            raise IomatError("IOMAT bloqueou a conexao (firewall).")
        except requests.exceptions.HTTPError as exc:
            raise IomatError(f"HTTP {res.status_code} ao chamar IOMAT: {exc}")
    raise IomatError("Esgotadas as tentativas de conexao com o IOMAT.")


def buscar_por_ano(termo: str, ano: int, exata: bool = True, max_paginas: int = 200) -> Iterator[Hit]:
    termo_api = f'"{termo}"' if exata else termo
    termo_url = urllib.parse.quote(termo)

    primeira = _request_json(BASE_BUSCA, {"q": termo_api, "y": ano})
    data = primeira.get("data", [{}])[0] if "data" in primeira else primeira
    total = data.get("hits", {}).get("total", 0)
    if isinstance(total, dict):
        total = total.get("value", 0)
    if not total:
        return

    tamanho_pagina = 10
    import math
    total_paginas = min(max_paginas, math.ceil(total / tamanho_pagina))
    vistos: set[str] = set()
    repeticoes = 0

    for pagina in range(1, total_paginas + 1):
        resp = _request_json(BASE_BUSCA, {"q": termo_api, "y": ano, "page": pagina})
        docs = (resp.get("data", [{}])[0] if "data" in resp else resp).get("hits", {}).get("hits", [])
        if not docs:
            break

        novos = 0
        for item in docs:
            src = item.get("_source", {})
            edicao_id = str(src.get("diario_id"))
            pagina_doc = src.get("pagina")
            key = f"{edicao_id}_{pagina_doc}"
            if key in vistos:
                continue
            vistos.add(key)
            novos += 1
            texto = src.get("conteudo", "")
            if isinstance(texto, list):
                texto = texto[0] if texto else ""
            yield Hit(
                edicao_id=edicao_id,
                tipo_edicao=int(src.get("tipo_edicao", 1)),
                pagina=int(pagina_doc or 0),
                ano=int(src.get("year", ano)),
                data_pub=str(src.get("data", "")),
                nome_edicao=str(item.get("suplemento") or edicao_id),
                texto_bruto=texto,
                link=(
                    f"https://iomat.mt.gov.br/portal/visualizacoes/pdf/{edicao_id}"
                    f"#/p:{pagina_doc}/e:{edicao_id}?find={termo_url}"
                ),
            )

        repeticoes = repeticoes + 1 if novos == 0 else 0
        if repeticoes >= 3:
            break
        time.sleep(0.5)


def baixar_pdf(tipo_edicao: int, edicao_id: str, pagina: int, destino: str) -> bool:
    url = f"{BASE_PDF}/{tipo_edicao}/edicoes/{edicao_id}/paginas/{pagina}"
    headers = {
        "accept": "application/pdf",
        "User-Agent": DEFAULT_HEADERS["User-Agent"],
    }
    try:
        res = requests.get(url, params={"formato": "pdf"}, headers=headers, timeout=30)
    except requests.RequestException:
        return False
    if res.status_code != 200 or "pdf" not in res.headers.get("Content-Type", "").lower():
        return False
    with open(destino, "wb") as fh:
        fh.write(res.content)
    return True


def buscar(termo: str, anos: Iterable[int], exata: bool = True) -> Iterator[Hit]:
    for ano in anos:
        yield from buscar_por_ano(termo, ano, exata=exata)
