"""Pipeline completo: extracao IOMAT + dedup + classificacao IA + download + indexacao + revisao."""
from __future__ import annotations

import logging
from decimal import Decimal
from pathlib import Path

from celery import shared_task
from django.conf import settings
from django.db import connection
from django.utils import timezone

from apps.documents.models import Classification, Document
from apps.reviews.models import Review
from apps.searches.models import PipelineStage, SearchJob, criar_stages

from .contexto import montar_contexto_delimitado
from .delimitador import Delimitador
from .iomat_client import IomatError, baixar_pdf, buscar_por_ano
from .openai_client import OpenAIClassifier

logger = logging.getLogger(__name__)

# Preco do modelo de classificacao (USD por 1M tokens). Vem das settings para poder
# ser ajustado ao modelo realmente usado (NAO assuma gpt-4o-mini). Veja
# OPENAI_PRECO_INPUT_POR_1M / OPENAI_PRECO_OUTPUT_POR_1M em config/settings/base.py.
PRECO_INPUT_POR_1M = Decimal(str(getattr(settings, "OPENAI_PRECO_INPUT_POR_1M", "0.15")))
PRECO_OUTPUT_POR_1M = Decimal(str(getattr(settings, "OPENAI_PRECO_OUTPUT_POR_1M", "0.60")))


def _pdf_dir() -> Path:
    destino = Path(settings.MEDIA_ROOT) / "pdfs"
    destino.mkdir(parents=True, exist_ok=True)
    return destino


def _cancelado(job: SearchJob) -> bool:
    job.refresh_from_db(fields=["status"])
    return job.status == SearchJob.Status.CANCELADO


def _parada_solicitada(job: SearchJob) -> str | None:
    """Retorna 'cancelado', 'pausado' ou None conforme o status atual no banco.

    Pausa e cancelamento param o worker na proxima iteracao; a diferenca e que
    a pausa NAO marca as etapas como falha (para permitir retomar de onde parou).
    """
    job.refresh_from_db(fields=["status"])
    if job.status == SearchJob.Status.CANCELADO:
        return "cancelado"
    if job.status == SearchJob.Status.PAUSADO:
        return "pausado"
    return None


def _nome_pdf(doc: Document) -> str:
    safe_edicao = "".join(c for c in str(doc.edicao_id) if c.isalnum() or c in "-_")
    return f"DOE_MT_{doc.ano}_Edicao_{safe_edicao}_Pagina_{doc.pagina}.pdf"


def _stage(job: SearchJob, codigo: str) -> PipelineStage:
    return PipelineStage.objects.get(search_job=job, codigo=codigo)


@shared_task(bind=True, name="core.process_search_job")
def process_search_job(self, search_job_id: int) -> None:
    job = (
        SearchJob.objects
        .select_related("criado_por__profile")
        .get(pk=search_job_id)
    )

    job.celery_task_id = (self.request.id or "") if getattr(self, "request", None) else ""
    job.started_at = timezone.now()
    job.status = SearchJob.Status.EXTRAINDO
    job.mensagem_erro = ""
    job.fase_atual = "Extraindo do IOMAT"
    job.mensagem_progresso = "Preparando para consultar a API do IOMAT..."
    job.ano_atual = job.ano_inicio
    job.doc_atual = 0
    job.save(update_fields=[
        "celery_task_id", "started_at", "status", "mensagem_erro",
        "fase_atual", "mensagem_progresso", "ano_atual", "doc_atual",
    ])

    # Garante que as 6 etapas existem pra este job
    criar_stages(job)

    stage_extracao      = _stage(job, "extracao")
    stage_dedup         = _stage(job, "dedup")
    stage_classificacao = _stage(job, "classificacao")
    stage_download      = _stage(job, "download")
    stage_indexacao     = _stage(job, "indexacao")
    stage_revisao       = _stage(job, "revisao")

    try:
        profile = job.criado_por.profile
        api_key = profile.get_openai_key()
        if not api_key:
            raise RuntimeError("Usuario nao configurou a chave de IA no perfil.")
        modelo = profile.modelo_efetivo
        if not modelo:
            raise RuntimeError("Usuario nao selecionou um modelo no perfil.")
        base_url = profile.base_url_efetivo

        # ---------------- STAGE 1: EXTRACAO ----------------
        stage_extracao.iniciar(
            total=(job.ano_fim - job.ano_inicio + 1),
            mensagem=f"Consultando IOMAT de {job.ano_inicio} a {job.ano_fim}",
        )
        documentos_do_job: list[Document] = []

        for i, ano in enumerate(range(job.ano_inicio, job.ano_fim + 1)):
            parada = _parada_solicitada(job)
            if parada == "pausado":
                logger.info("Job %s pausado durante extracao", job.pk)
                return
            if parada == "cancelado":
                logger.info("Job %s cancelado durante extracao", job.pk)
                stage_extracao.falhar("Cancelado pelo usuario")
                return
            job.ano_atual = ano
            job.mensagem_progresso = f"Consultando IOMAT para o ano {ano}..."
            job.save(update_fields=["ano_atual", "mensagem_progresso"])
            try:
                for hit in buscar_por_ano(job.termo, ano, exata=job.busca_exata):
                    doc, _ = Document.objects.update_or_create(
                        edicao_id=hit.edicao_id,
                        pagina=hit.pagina,
                        defaults={
                            "tipo_edicao": hit.tipo_edicao,
                            "ano": hit.ano,
                            "nome_edicao": hit.nome_edicao,
                            "data_pub": hit.data_pub,
                            "link_oficial": hit.link,
                            "texto_bruto": hit.texto_bruto,
                        },
                    )
                    documentos_do_job.append(doc)
                    if len(documentos_do_job) % 5 == 0:
                        job.total_extraidos = len(documentos_do_job)
                        job.mensagem_progresso = (
                            f"Ano {ano}: {len(documentos_do_job)} documentos extraidos ate agora."
                        )
                        job.save(update_fields=["total_extraidos", "mensagem_progresso"])
            except IomatError as exc:
                logger.warning("Ano %s falhou: %s", ano, exc)
                job.mensagem_progresso = f"Ano {ano} falhou ({exc}); seguindo."
                job.save(update_fields=["mensagem_progresso"])
            stage_extracao.tick(feitos=i + 1, mensagem=f"ano {ano} ok")

        job.total_extraidos = len(documentos_do_job)
        job.save(update_fields=["total_extraidos"])
        stage_extracao.concluir(mensagem=f"{job.total_extraidos} documentos extraidos")

        if not documentos_do_job:
            stage_dedup.pular("sem documentos")
            stage_classificacao.pular("sem documentos")
            stage_download.pular("sem documentos")
            stage_indexacao.pular("sem documentos")
            stage_revisao.pular("sem documentos")
            job.status = SearchJob.Status.CONCLUIDO
            job.finished_at = timezone.now()
            job.save(update_fields=["status", "finished_at"])
            return

        # ---------------- STAGE 2: DEDUP ----------------
        stage_dedup.iniciar(total=len(documentos_do_job), mensagem="verificando reaproveitaveis")
        reaproveitados_pks: set[int] = set()
        ja_classificados_pks: set[int] = set()
        for i, doc in enumerate(documentos_do_job):
            if Review.objects.filter(document=doc).exists():
                reaproveitados_pks.add(doc.pk)
            elif (
                not job.forcar_reclassificacao
                and Classification.objects.filter(
                    document=doc, termo_buscado__iexact=job.termo
                ).exists()
            ):
                ja_classificados_pks.add(doc.pk)
            if (i + 1) % 20 == 0:
                stage_dedup.tick(feitos=i + 1)
        job.total_reaproveitados = len(reaproveitados_pks)
        job.save(update_fields=["total_reaproveitados"])
        stage_dedup.concluir(
            mensagem=f"{len(reaproveitados_pks)} reaproveitados, {len(ja_classificados_pks)} ja classificados"
        )

        # ---------------- STAGE 3: CLASSIFICACAO ----------------
        pendentes = [
            d for d in documentos_do_job
            if d.pk not in reaproveitados_pks and d.pk not in ja_classificados_pks
        ]
        job.status = SearchJob.Status.CLASSIFICANDO
        job.fase_atual = f"Classificando com IA ({modelo})"
        job.mensagem_progresso = f"Iniciando classificacao de {len(pendentes)} documentos..."
        job.doc_atual = 0
        job.save(update_fields=["status", "fase_atual", "mensagem_progresso", "doc_atual"])

        stage_classificacao.iniciar(total=len(pendentes), mensagem=f"modelo {modelo}")
        # Download roda em paralelo logico com a classificacao (inline por doc).
        stage_download.iniciar(total=0, mensagem="baixando relevantes e duvidosos")

        classifier = OpenAIClassifier(api_key=api_key, model=modelo, base_url=base_url)
        pdf_dir = _pdf_dir()
        # Contexto multipagina: expande paginas vizinhas ate as fronteiras do ato.
        # Por padrao classificamos a pagina isolada (maior concordancia com humano).
        # Se o job pedir, usamos o DELIMITADOR (LLM local gpt-oss) para identificar
        # quais paginas pertencem ao mesmo ato antes de classificar.
        usar_delimitador = bool(getattr(job, "usar_delimitador", False))
        delimitador = None
        if usar_delimitador:
            delimitador = Delimitador(
                base_url=getattr(settings, "DELIMITADOR_BASE_URL", ""),
                api_key=getattr(settings, "DELIMITADOR_API_KEY", ""),
                modelo=getattr(settings, "DELIMITADOR_MODELO", ""),
                verify_ssl=getattr(settings, "DELIMITADOR_VERIFY_SSL", False),
                num_ctx=getattr(settings, "DELIMITADOR_NUM_CTX", 16384),
                trecho_limite=getattr(settings, "DELIMITADOR_TRECHO", 6000),
                endpoint=getattr(settings, "DELIMITADOR_ENDPOINT", "/ollama/api/chat"),
            )
            if not delimitador.configurado:
                logger.warning("Delimitador pedido mas nao configurado; classificando por pagina.")
                usar_delimitador = False
                delimitador = None
        delim_janela = int(getattr(settings, "DELIMITADOR_JANELA", 2))
        ctx_cache: dict = {}
        tokens_in_total = 0
        tokens_out_total = 0
        downloads_feitos = 0
        downloads_alvo = 0

        total_docs = len(pendentes)
        for idx, doc in enumerate(pendentes):
            parada = _parada_solicitada(job)
            if parada == "pausado":
                logger.info("Job %s pausado durante classificacao (doc %s/%s)",
                            job.pk, idx + 1, total_docs)
                job.mensagem_progresso = (
                    f"Pausado em {idx + 1}/{total_docs}. Retome para continuar de onde parou."
                )
                job.save(update_fields=["mensagem_progresso"])
                return
            if parada == "cancelado":
                logger.info("Job %s cancelado durante classificacao", job.pk)
                stage_classificacao.falhar("Cancelado pelo usuario")
                stage_download.falhar("Cancelado pelo usuario")
                return

            job.doc_atual = idx + 1
            job.mensagem_progresso = (
                f"Classificando doc {idx + 1}/{total_docs} "
                f"(edicao {doc.edicao_id}, pag {doc.pagina}, ano {doc.ano})"
            )
            job.save(update_fields=["doc_atual", "mensagem_progresso"])

            paginas_ctx = ""
            com_contexto = False
            try:
                if usar_delimitador:
                    ctx = montar_contexto_delimitado(
                        tipo_edicao=doc.tipo_edicao,
                        edicao_id=doc.edicao_id,
                        pagina=doc.pagina,
                        texto_alvo=doc.texto_bruto or "",
                        delimitador=delimitador,
                        janela=delim_janela,
                        cache=ctx_cache,
                    )
                    paginas_ctx = ",".join(str(p) for p in ctx["paginas"])
                    # so e "com contexto" se o ato realmente vazou para outras paginas
                    com_contexto = len(ctx["paginas"]) > 1
                    multipag = com_contexto
                    c = classifier.classificar(
                        ctx["texto"] if multipag else (doc.texto_bruto or ""),
                        job.termo,
                        multipagina=multipag,
                    )
                else:
                    c = classifier.classificar(doc.texto_bruto or "", job.termo)
            except Exception as exc:  # noqa: BLE001
                logger.exception("Erro classificando doc %s", doc.pk)
                job.total_erros += 1
                job.save(update_fields=["total_erros"])
                stage_classificacao.tick(feitos=idx + 1, mensagem=f"erro doc {doc.pk}")
                continue

            Classification.objects.create(
                document=doc,
                search_job=job,
                termo_buscado=job.termo,
                classificacao=c.classificacao,
                tipo_ato=c.tipo_ato,
                justificativa=c.justificativa,
                prompt_enviado=c.prompt_usuario,
                resposta_crua=c.resposta_crua,
                modelo_ia=classifier.model,
                tokens_input=c.tokens_input,
                tokens_output=c.tokens_output,
                com_contexto=com_contexto,
                paginas_contexto=paginas_ctx,
            )
            tokens_in_total += c.tokens_input or 0
            tokens_out_total += c.tokens_output or 0

            # Download: apenas relevantes e duvidosos
            if c.classificacao in {"super_relevante", "relevante", "duvidoso"}:
                downloads_alvo += 1
                stage_download.itens_total = downloads_alvo
                nome = _nome_pdf(doc)
                destino = pdf_dir / nome
                if not destino.exists():
                    try:
                        baixar_pdf(doc.tipo_edicao, doc.edicao_id, doc.pagina, str(destino))
                    except Exception:  # noqa: BLE001
                        logger.exception("Falha ao baixar PDF do doc %s", doc.pk)
                if destino.exists():
                    if not doc.caminho_pdf:
                        doc.caminho_pdf = f"pdfs/{nome}"
                        doc.save(update_fields=["caminho_pdf"])
                    downloads_feitos += 1
                stage_download.tick(
                    feitos=downloads_feitos,
                    mensagem=f"{downloads_feitos}/{downloads_alvo} PDFs",
                )
                # persiste o novo total
                stage_download.save(update_fields=["itens_total"])

            if c.classificacao in {"super_relevante", "relevante"}:
                job.total_relevantes += 1
            elif c.classificacao == "duvidoso":
                job.total_duvidosos += 1
            else:
                job.total_descartados += 1

            stage_classificacao.tick(
                feitos=idx + 1,
                mensagem=f"{c.classificacao} [{c.tipo_ato[:40]}]",
            )

            if (idx + 1) % 5 == 0:
                if profile.provider == profile.Provider.OPENAI:
                    job.custo_estimado_usd = (
                        (Decimal(tokens_in_total) / Decimal(1_000_000)) * PRECO_INPUT_POR_1M
                        + (Decimal(tokens_out_total) / Decimal(1_000_000)) * PRECO_OUTPUT_POR_1M
                    ).quantize(Decimal("0.0001"))
                job.save(update_fields=[
                    "total_relevantes", "total_duvidosos", "total_descartados",
                    "total_erros", "total_reaproveitados", "custo_estimado_usd",
                ])

        stage_classificacao.concluir(
            mensagem=(
                f"{job.total_relevantes} rel / {job.total_duvidosos} duv / "
                f"{job.total_descartados} desc / {job.total_erros} erros"
            )
        )
        if downloads_alvo == 0:
            stage_download.pular("nenhum relevante/duvidoso")
        else:
            stage_download.concluir(mensagem=f"{downloads_feitos}/{downloads_alvo} PDFs baixados")

        # ---------------- STAGE 5: INDEXACAO ----------------
        if connection.vendor == "postgresql":
            stage_indexacao.iniciar(total=len(documentos_do_job), mensagem="SearchVector portugues")
            try:
                from django.contrib.postgres.search import SearchVector
                pks = [d.pk for d in documentos_do_job]
                (Document.objects
                    .filter(pk__in=pks)
                    .update(search_vector=SearchVector("texto_bruto", config="portuguese")))
                stage_indexacao.concluir(mensagem=f"{len(pks)} documentos indexados")
            except Exception as exc:  # noqa: BLE001
                logger.exception("Indexacao full-text falhou")
                stage_indexacao.falhar(f"erro: {exc}")
        else:
            stage_indexacao.pular(f"requer Postgres (atual: {connection.vendor})")

        # ---------------- STAGE 6: REVISAO (humana - fica queued) ----------------
        stage_revisao.itens_total = job.total_duvidosos
        stage_revisao.mensagem = f"{job.total_duvidosos} duvidosos aguardando"
        stage_revisao.save(update_fields=["itens_total", "mensagem"])

        # ---------------- FINALIZACAO ----------------
        if profile.provider == profile.Provider.OPENAI:
            job.custo_estimado_usd = (
                (Decimal(tokens_in_total) / Decimal(1_000_000)) * PRECO_INPUT_POR_1M
                + (Decimal(tokens_out_total) / Decimal(1_000_000)) * PRECO_OUTPUT_POR_1M
            ).quantize(Decimal("0.0001"))
        else:
            job.custo_estimado_usd = None
        job.status = SearchJob.Status.CONCLUIDO
        job.fase_atual = "Concluido"
        job.mensagem_progresso = (
            f"Pipeline concluido: {job.total_relevantes} relevantes, "
            f"{job.total_duvidosos} duvidosos, {job.total_descartados} descartados, "
            f"{job.total_erros} erros."
        )
        job.finished_at = timezone.now()
        job.save()

    except Exception as exc:  # noqa: BLE001
        logger.exception("SearchJob %s falhou", job.pk)
        # marca como falha qualquer stage que ainda estava rodando
        for st in PipelineStage.objects.filter(
            search_job=job, estado=PipelineStage.Estado.RUNNING,
        ):
            st.falhar(str(exc)[:240])
        job.status = SearchJob.Status.FALHOU
        job.mensagem_erro = str(exc)[:2000]
        job.fase_atual = "Falhou"
        job.mensagem_progresso = f"Erro: {str(exc)[:250]}"
        job.finished_at = timezone.now()
        job.save(update_fields=[
            "status", "mensagem_erro", "finished_at", "fase_atual", "mensagem_progresso",
        ])
