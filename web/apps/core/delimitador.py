"""Delimitador de atos via LLM local (OpenWebUI / gpt-oss).

Variante B do nosso desenho: o modelo local NAO reescreve texto e NAO classifica
relevancia. Ele apenas devolve QUAIS PAGINAS (numeros) pertencem ao mesmo ato da
pagina-alvo. Depois recortamos o texto OCR ORIGINAL dessas paginas (sem alucinacao)
e mandamos ao classificador (GPT).

Validado em 30 casos com gabarito humano: gpt-oss:20b acertou ~87%, com erros
majoritariamente "seguros" (1 pagina a mais/menos), nunca arrastando atos distintos
de forma a inflar falsos positivos.

Config (settings):
  DELIMITADOR_BASE_URL   - ex: "https://tutoria.cba.ifmt.edu.br"
  DELIMITADOR_API_KEY    - chave do OpenWebUI
  DELIMITADOR_MODELO     - ex: "gpt-oss:20b"
  DELIMITADOR_VERIFY_SSL - bool (default False; o servidor institucional tem cert invalido)
"""
from __future__ import annotations

import json
import logging
import re
import time

import requests

try:  # urllib3 pode emitir warnings de SSL desabilitado; silencia.
    import urllib3
    urllib3.disable_warnings()
except Exception:  # noqa: BLE001
    pass

logger = logging.getLogger(__name__)

_SYS = (
    "Voce delimita atos de Diario Oficial. Pense breve e finalize com uma "
    'linha JSON {"paginas":[...]}.'
)


def _prompt_usuario(pagina_alvo: int, blocos: str) -> str:
    return (
        f"Paginas de um Diario Oficial. A pagina-alvo e a {pagina_alvo}. "
        f"Um ato (LEI, DECRETO, PORTARIA, RESOLUCAO, EDITAL, RELATORIO, ACORDAO, "
        f"INSTRUCAO NORMATIVA) comeca num cabecalho-titulo em MAIUSCULAS e termina "
        f"quando comeca OUTRO cabecalho-titulo diferente. Citacoes a leis no meio "
        f"do texto NAO contam. Quais paginas formam o MESMO ato/documento da pagina "
        f"{pagina_alvo} (a alvo + adjacentes que sao continuacao)?\n\n{blocos}\n\n"
        f'Finalize com {{"paginas":[...]}}'
    )


def _trecho(txt: str, limite: int = 1100) -> str:
    txt = " ".join((txt or "").split())
    if len(txt) <= limite:
        return txt
    meio = limite // 2
    return "INICIO: " + txt[:meio] + " ... FIM: " + txt[-meio:]


def _extrai_paginas(resposta: str) -> list[int] | None:
    """Extrai a lista de paginas do JSON, tolerando <think> e markdown."""
    s = re.sub(r"<think>.*?</think>", "", resposta, flags=re.DOTALL)
    s = s.replace("```json", "").replace("```", "")
    for m in reversed(list(re.finditer(r"\{[^{}]*\}", s))):
        try:
            j = json.loads(m.group(0))
            if "paginas" in j and isinstance(j["paginas"], list):
                return [int(x) for x in j["paginas"] if str(x).strip().lstrip("-").isdigit()]
        except (json.JSONDecodeError, ValueError, TypeError):
            continue
    return None


class Delimitador:
    """Cliente do LLM local que delimita as paginas de um ato."""

    def __init__(self, base_url: str, api_key: str, modelo: str, verify_ssl: bool = False,
                 num_ctx: int = 8192, trecho_limite: int = 2500,
                 endpoint: str = "/ollama/api/chat"):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.modelo = modelo
        self.verify_ssl = verify_ssl
        self.num_ctx = int(num_ctx)
        self.trecho_limite = int(trecho_limite)
        # Endpoint NATIVO do Ollama (passthrough do OpenWebUI). Ao contrario do
        # /api/chat/completions (OpenAI-compat, que IGNORA options.num_ctx e capa
        # o prompt em 4096 tokens), o /ollama/api/chat RESPEITA options.num_ctx.
        self.endpoint = endpoint

    @property
    def configurado(self) -> bool:
        return bool(self.base_url and self.api_key and self.modelo)

    @staticmethod
    def _extrai_conteudo(j: dict) -> str:
        """Tolera resposta nativa do Ollama (message.content) e OpenAI-compat (choices)."""
        if isinstance(j.get("message"), dict):
            return j["message"].get("content") or ""
        try:
            return j["choices"][0]["message"]["content"] or ""
        except (KeyError, IndexError, TypeError):
            return ""

    def _chat(self, user: str, timeout: int = 300, retries: int = 2) -> str:
        url = f"{self.base_url}{self.endpoint}"
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        payload = {
            "model": self.modelo,
            "messages": [
                {"role": "system", "content": _SYS},
                {"role": "user", "content": user},
            ],
            "temperature": 0,
            "stream": False,
            "options": {"num_ctx": self.num_ctx, "temperature": 0},
        }
        ultimo = None
        for tentativa in range(retries):
            try:
                r = requests.post(url, headers=headers, json=payload,
                                  timeout=timeout, verify=self.verify_ssl)
                r.raise_for_status()
                return self._extrai_conteudo(r.json())
            except Exception as exc:  # noqa: BLE001
                ultimo = exc
                if tentativa < retries - 1:
                    time.sleep(3)
                    continue
        raise RuntimeError(f"Delimitador falhou: {ultimo}")

    def delimitar(self, pagina_alvo: int, paginas_texto: dict[int, str]) -> list[int] | None:
        """Recebe {numero_pagina: texto} e devolve a lista de paginas do ato.

        Retorna None se nao conseguir uma resposta valida (o chamador faz fallback).
        A lista retornada e sempre filtrada para o conjunto de paginas oferecidas
        e garante incluir a pagina-alvo.
        """
        if not self.configurado:
            return None
        oferecidas = sorted(paginas_texto.keys())
        blocos = []
        for p in oferecidas:
            marca = " (ALVO)" if p == pagina_alvo else ""
            blocos.append(f"[PAGINA {p}{marca}]\n{_trecho(paginas_texto[p], self.trecho_limite)}")
        try:
            resp = self._chat(_prompt_usuario(pagina_alvo, "\n\n".join(blocos)))
        except Exception:  # noqa: BLE001
            logger.exception("Delimitador: erro na chamada ao LLM local")
            return None
        paginas = _extrai_paginas(resp)
        if not paginas:
            logger.warning("Delimitador: resposta sem JSON valido: %r", resp[:200])
            return None
        # saneia: so paginas oferecidas, com a alvo garantida, ordenado
        validas = sorted({p for p in paginas if p in paginas_texto} | {pagina_alvo})
        return validas
