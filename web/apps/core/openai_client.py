"""Wrapper fino de classificacao (OpenAI + OpenWebUI) em 4 estados."""
from __future__ import annotations

import json
import logging
import re
import time
from dataclasses import dataclass

import httpx
from openai import OpenAI

logger = logging.getLogger(__name__)

PROMPT_SISTEMA = """Voce e um pesquisador academico rigoroso avaliando o Diario Oficial de Mato Grosso.
Projeto: "Mapeamento da legislacao da EDUCACAO PROFISSIONAL E TECNOLOGICA / ENSINO TECNICO".

==================== ESCOPO (LEIA PRIMEIRO) ====================
O objeto da pesquisa e a EDUCACAO PROFISSIONAL E TECNOLOGICA / ENSINO TECNICO em
QUALQUER NIVEL (tanto NIVEL MEDIO quanto SUPERIOR). Isto INCLUI (sao RELEVANTES):
- Ensino tecnico de nivel medio / habilitacao tecnica de 2o grau (ex: Tecnico em
  Contabilidade, Tecnico em Agrimensura, Tecnico em Enfermagem, Tecnico Agricola).
- Cursos profissionalizantes e de educacao profissional (formacao para o trabalho).
- Cursos Superiores de Tecnologia (CST), tecnologo, graduacao tecnologica.
- Educacao profissional de nivel superior (pos-medio/terciario).
- Instituicoes que ofertam esses cursos (escolas tecnicas, CEFET, Escola Agrotecnica,
  institutos/faculdades de tecnologia, centros de educacao profissional, UNEMAT/IFMT
  em cursos tecnicos ou tecnologicos).
- Atos sobre esses cursos/instituicoes: criacao, autorizacao, reconhecimento,
  regulamentacao, curriculo/grade, regimento, convenio educacional, denominacao de
  escola tecnica, plano de curso.

NAO faz parte do escopo (estes sao IRRELEVANTES, mesmo citando "ensino", "tecnico",
"profissional" ou "curso"):
- Ensino fundamental / 1o grau / educacao basica comum.
- Ensino medio REGULAR/PROPEDEUTICO (nao-tecnico), curso normal/magisterio comum.
- Cursos livres genericos sem carater profissionalizante claro.
- Edital de concurso publico que apenas EXIGE um curso, ou que oferece curso de
  formacao para o proprio cargo (ex: curso de formacao de policiais) — isso NAO cria
  nem regulamenta educacao profissional; classifique como IRRELEVANTE.
- Atos administrativos de pessoal (nomeacao, exoneracao, ferias, licenca, diaria).
- Orcamento, balanco, demonstrativo, licitacao, contrato administrativo generico.
- Atas de empresas, sindicatos ou associacoes sem relacao com oferta de ensino tecnico.
- Mencao tangencial/incidental (ex: terreno doado para futura escola, noticia, rubrica
  orcamentaria que so cita "educacao profissional"). Mencao NAO e ato sobre o tema.

REGRA DE OURO: marque como relevante quando o ato TRATAR de um curso ou instituicao de
educacao profissional/tecnica (qualquer nivel). Na duvida entre o tema e algo apenas
administrativo/tangencial, use "duvidoso" (vai para revisao humana). NUNCA invente
conteudo que nao esteja no texto.

==================== NIVEIS ====================
- "super_relevante": ato CENTRAL e inequivoco que cria, autoriza, reconhece ou
  regulamenta DIRETAMENTE um curso tecnico/profissionalizante/tecnologico ou uma
  instituicao desse tipo (ex: lei que cria escola tecnica; resolucao do CEE/MT que
  autoriza/reconhece curso tecnico ou CST; decreto que cria centro de educacao
  profissional).

- "relevante": trata de educacao profissional/tecnica (qualquer nivel) de forma
  complementar ou administrativa ligada ao ensino (curriculo, regimento, convenio
  educacional, portaria sobre o curso, mudanca de denominacao de escola tecnica,
  plano de curso, reconhecimento de concluintes de curso tecnico).

- "duvidoso": ha indicios do tema mas o texto e ambiguo/truncado, OU pode ser apenas
  tangencial/administrativo sem tratar do curso em si. Use para mandar a revisao humana.

- "irrelevante": tudo fora do escopo acima — ensino fundamental/medio regular nao-tecnico,
  edital de concurso, nomeacoes, orcamentos, licitacoes, atas comerciais, mencoes
  tangenciais, etc.

IMPORTANTE SOBRE O CONTEXTO:
O texto pode conter VARIAS paginas do Diario Oficial. A PAGINA-ALVO estara demarcada; as
demais sao apenas contexto, pois um ato pode comecar/terminar em outra pagina. Use o
contexto para entender o ato completo, MAS a classificacao se refere ao ATO DA PAGINA-ALVO.
ATENCAO: nao deixe o contexto inflar a relevancia — se as paginas vizinhas tratam de
OUTROS assuntos (mesmo que citem ensino), isso NAO torna a pagina-alvo relevante. A
classificacao e sobre o ATO DA PAGINA-ALVO. Baseie-se SO no que esta escrito; nunca
invente cursos, instituicoes ou conteudos que nao aparecam no texto.

TIPOS DE ATO ESPERADOS (use exatamente um destes quando aplicavel):
Constituicao, Emenda Constitucional, Lei, Lei Complementar, Lei Ordinaria, Lei Delegada, Medida Provisoria, Decreto Legislativo, Decreto, Decreto-Lei, Resolucao, Portaria, Instrucao Normativa, Regimento, Regulamento, Estatuto, Diretrizes Curriculares, Plano.
Se nenhum tipo se aplica (conteudo irrelevante), use "Outro" seguido de descricao curta (ex: "Outro - Licitacao").

REGRAS DE SAIDA (obrigatorias):
1. Responda APENAS com um objeto JSON valido. Nada antes, nada depois.
2. NAO use blocos de codigo markdown (sem crases, sem ```json).
3. NAO escreva frases explicativas fora do JSON.

Formato exato:
{"classificacao": "super_relevante|relevante|duvidoso|irrelevante", "tipo_ato": "<tipo da lista acima>", "justificativa": "motivo curto e objetivo"}"""


class ClassificacaoParseError(Exception):
    """Modelo retornou algo que nao consegui interpretar como JSON."""


@dataclass
class Classificacao:
    classificacao: str
    tipo_ato: str
    justificativa: str
    prompt_usuario: str
    resposta_crua: str
    tokens_input: int | None = None
    tokens_output: int | None = None


# ---------- Parse tolerante ----------

_FENCE_RE = re.compile(r"```(?:json|JSON)?\s*(.*?)```", re.DOTALL)


def extrair_json(texto: str) -> dict:
    """Tenta extrair um objeto JSON de uma resposta de LLM, mesmo com lixo ao redor.

    Estrategias em ordem:
    1. json.loads direto (caso feliz)
    2. Remover fences markdown ```json ... ``` e tentar
    3. Procurar o primeiro `{` ... ultimo `}` e tentar
    """
    if not texto:
        raise ClassificacaoParseError("resposta vazia")

    s = texto.strip()

    try:
        return json.loads(s)
    except json.JSONDecodeError:
        pass

    m = _FENCE_RE.search(s)
    if m:
        candidato = m.group(1).strip()
        try:
            return json.loads(candidato)
        except json.JSONDecodeError:
            pass

    ini = s.find("{")
    fim = s.rfind("}")
    if ini >= 0 and fim > ini:
        candidato = s[ini:fim + 1]
        try:
            return json.loads(candidato)
        except json.JSONDecodeError:
            pass

    raise ClassificacaoParseError(f"nao consegui extrair JSON. Trecho: {s[:200]!r}")


# ---------- Classificador ----------

class OpenAIClassifier:
    def __init__(self, api_key: str, model: str = "gpt-4o-mini", base_url: str | None = None,
                 verify_ssl: bool | None = None):
        kwargs = {"api_key": api_key}
        if base_url:
            kwargs["base_url"] = base_url
            # OpenWebUI / servidores institucionais (ex.: IFMT) costumam ter certificado
            # SSL invalido. O SDK da OpenAI usa httpx, que verifica SSL por padrao, e a
            # conexao falha com APIConnectionError. Quando ha base_url custom, desligamos
            # a verificacao (mesma postura do delimitador, que usa requests verify=False).
            if verify_ssl is None:
                verify_ssl = False
            kwargs["http_client"] = httpx.Client(verify=verify_ssl, timeout=httpx.Timeout(120.0))
        self.client = OpenAI(**kwargs)
        self.model = model
        self.is_openwebui = bool(base_url)
        self._usar_temperatura = True

    def _call(self, prompt_usuario: str, forcar_json: bool):
        kwargs = dict(
            model=self.model,
            messages=[
                {"role": "system", "content": PROMPT_SISTEMA},
                {"role": "user", "content": prompt_usuario},
            ],
        )
        if self._usar_temperatura:
            kwargs["temperature"] = 0.0
        if forcar_json:
            kwargs["response_format"] = {"type": "json_object"}
        return self.client.chat.completions.create(**kwargs)

    def classificar(
        self,
        texto: str,
        palavra_chave: str,
        retries: int = 3,
        multipagina: bool = False,
    ) -> Classificacao:
        if multipagina:
            prompt_usuario = (
                f"Termo de busca que retornou a pagina-alvo: '{palavra_chave}'.\n\n"
                f"Conteudo (a PAGINA-ALVO esta demarcada; as demais sao contexto):\n{texto}"
            )
        else:
            prompt_usuario = f"Palavra-chave: '{palavra_chave}'.\n\nTexto:\n{texto}"
        ultimo_erro: Exception | None = None
        # Em OpenAI oficial comecamos forcando JSON. Em OpenWebUI comecamos sem.
        forcar_json = not self.is_openwebui

        for tentativa in range(retries):
            try:
                try:
                    response = self._call(prompt_usuario, forcar_json=forcar_json)
                except Exception as exc:  # noqa: BLE001
                    msg = str(exc).lower()
                    ajustou = False
                    if self._usar_temperatura and "temperature" in msg:
                        logger.warning("Modelo nao suporta temperature=0; removendo. Detalhe: %s", exc)
                        self._usar_temperatura = False
                        ajustou = True
                    if forcar_json and ("response_format" in msg or "unsupported" in msg):
                        logger.warning("Servidor rejeitou response_format; caindo para modo livre. Detalhe: %s", exc)
                        forcar_json = False
                        ajustou = True
                    if ajustou:
                        response = self._call(prompt_usuario, forcar_json=forcar_json)
                    else:
                        raise

                resposta_crua = response.choices[0].message.content or ""

                try:
                    parsed = extrair_json(resposta_crua)
                except ClassificacaoParseError as exc:
                    logger.warning(
                        "Resposta do modelo nao e JSON (tentativa %d/%d). Erro: %s. Resposta crua: %r",
                        tentativa + 1, retries, exc, resposta_crua[:500],
                    )
                    # Se ainda temos retries e estamos em modo livre, tenta de novo com reforco
                    if tentativa < retries - 1:
                        # reforca instrucao no proximo prompt
                        prompt_usuario = (
                            f"{prompt_usuario}\n\n"
                            "IMPORTANTE: responda APENAS o JSON, sem crases, sem explicacao."
                        )
                        continue
                    # Falha final: propaga pra task marcar como erro (nao como duvidoso silencioso)
                    raise ClassificacaoParseError(
                        f"Modelo nao retornou JSON valido apos {retries} tentativas. "
                        f"Ultima resposta crua (trecho): {resposta_crua[:300]!r}"
                    )

                classe = (parsed.get("classificacao") or "").lower().strip()
                if classe not in {"super_relevante", "relevante", "duvidoso", "irrelevante"}:
                    # JSON valido mas SEM o campo 'classificacao' esperado (ex.: modelo
                    # fraco devolveu {"resumo": ...}). Isso e FALHA DE FORMATO, nao "duvida":
                    # tenta de novo com reforco e, se persistir, conta como ERRO. Antes isso
                    # virava "duvidoso" silenciosamente, o que mascarava modelos ruins e
                    # contaminava o benchmark (dezenas de duvidosos falsos).
                    logger.warning(
                        "Resposta sem 'classificacao' valida (tentativa %d/%d). Parsed: %r",
                        tentativa + 1, retries, parsed,
                    )
                    if tentativa < retries - 1:
                        prompt_usuario = (
                            f"{prompt_usuario}\n\n"
                            "IMPORTANTE: devolva SOMENTE o JSON com a chave \"classificacao\" "
                            "valendo exatamente super_relevante, relevante, duvidoso ou irrelevante."
                        )
                        continue
                    raise ClassificacaoParseError(
                        f"Modelo nao retornou 'classificacao' valida apos {retries} tentativas. "
                        f"Ultima resposta (trecho): {resposta_crua[:300]!r}"
                    )

                usage = getattr(response, "usage", None)
                return Classificacao(
                    classificacao=classe,
                    tipo_ato=(parsed.get("tipo_ato") or "")[:120],
                    justificativa=(parsed.get("justificativa") or "")[:2000],
                    prompt_usuario=prompt_usuario,
                    resposta_crua=resposta_crua,
                    tokens_input=getattr(usage, "prompt_tokens", None) if usage else None,
                    tokens_output=getattr(usage, "completion_tokens", None) if usage else None,
                )
            except ClassificacaoParseError:
                raise
            except Exception as exc:  # noqa: BLE001
                ultimo_erro = exc
                if "Rate limit" in str(exc) or "429" in str(exc):
                    time.sleep(3)
                    continue
                raise
        raise RuntimeError(f"Falha ao classificar apos {retries} tentativas: {ultimo_erro}")
