from celery.result import AsyncResult
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods

from apps.accounts.models import UserProfile
from apps.core.dispatcher import dispatch_search_job

from .forms import SearchJobForm
from .models import SearchJob


@login_required
def search_list(request):
    jobs = SearchJob.objects.select_related("criado_por").all()
    return render(request, "searches/list.html", {"jobs": jobs})


@login_required
@require_http_methods(["GET", "POST"])
def search_new(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    if request.method == "POST":
        form = SearchJobForm(request.POST)
        if form.is_valid():
            if not profile.has_openai_key:
                messages.error(request, "Configure sua chave OpenAI no perfil antes de iniciar uma busca.")
                return redirect("accounts:profile")
            job = form.save(commit=False)
            job.criado_por = request.user
            job.fase_atual = "Aguardando worker..."
            job.mensagem_progresso = "Job criado. Dispatch iniciado."
            job.save()
            modo, ident = dispatch_search_job(job.pk)
            if modo == "celery":
                job.celery_task_id = ident
                job.save(update_fields=["celery_task_id"])
                messages.success(request, "Pipeline enfileirado no Celery. Acompanhe abaixo.")
            else:
                messages.info(
                    request,
                    "Redis indisponivel: rodando em thread local. O progresso aparece abaixo em tempo real.",
                )
            return redirect(job.get_absolute_url())
    else:
        form = SearchJobForm(initial={"ano_inicio": 2000, "ano_fim": 2008})
    return render(request, "searches/new.html", {"form": form})


@login_required
def search_compare(request):
    """Compara, documento a documento, as classificacoes geradas por varias buscas.

    Uso: /buscas/comparar/?jobs=19,31,32  (default: as 3 ultimas concluidas)
    Permite filtrar so os documentos onde as buscas divergem.
    """
    from apps.documents.models import Classification

    param = request.GET.get("jobs", "").strip()
    if param:
        ids = [int(x) for x in param.split(",") if x.strip().isdigit()]
    else:
        ids = list(
            SearchJob.objects.filter(status=SearchJob.Status.CONCLUIDO)
            .order_by("-id").values_list("id", flat=True)[:3]
        )
        ids = sorted(ids)

    jobs = list(SearchJob.objects.filter(id__in=ids))
    jobs_por_id = {j.id: j for j in jobs}
    ids = [i for i in ids if i in jobs_por_id]  # mantem ordem, so validos

    # mapa: doc_id -> {job_id -> Classification (a mais recente daquele job)}
    por_doc: dict[int, dict] = {}
    docs_meta: dict[int, object] = {}
    cls = (
        Classification.objects
        .filter(search_job_id__in=ids)
        .select_related("document")
        .order_by("created_at")  # a ultima sobrescreve
    )
    for c in cls:
        por_doc.setdefault(c.document_id, {})[c.search_job_id] = c
        docs_meta[c.document_id] = c.document

    so_divergentes = request.GET.get("divergentes") == "1"

    def classe_efetiva(c):
        return c.classificacao if c else None

    linhas = []
    n_divergentes = 0
    for doc_id, mapa in por_doc.items():
        classes = [classe_efetiva(mapa.get(i)) for i in ids]
        presentes = [x for x in classes if x]
        divergente = len(set(presentes)) > 1
        if divergente:
            n_divergentes += 1
        if so_divergentes and not divergente:
            continue
        linhas.append({
            "doc": docs_meta[doc_id],
            "cells": [mapa.get(i) for i in ids],
            "divergente": divergente,
        })

    linhas.sort(key=lambda r: (r["doc"].ano, str(r["doc"].edicao_id), r["doc"].pagina))

    return render(request, "searches/compare.html", {
        "jobs": [jobs_por_id[i] for i in ids],
        "linhas": linhas,
        "total": len(por_doc),
        "n_divergentes": n_divergentes,
        "so_divergentes": so_divergentes,
        "ids_param": ",".join(str(i) for i in ids),
        "todas_buscas": SearchJob.objects.filter(status=SearchJob.Status.CONCLUIDO).order_by("-id"),
    })


@login_required
def search_detail(request, pk: int):
    job = get_object_or_404(SearchJob, pk=pk)
    return render(request, "searches/detail.html", {"job": job})


@login_required
def search_progress(request, pk: int):
    job = get_object_or_404(SearchJob, pk=pk)
    response = render(request, "searches/_progress.html", {"job": job})
    if not job.em_andamento:
        response["HX-Trigger"] = "pipelineConcluido"
    return response


@login_required
@require_http_methods(["POST"])
def search_cancel(request, pk: int):
    job = get_object_or_404(SearchJob, pk=pk)
    if job.em_andamento:
        if job.celery_task_id:
            try:
                AsyncResult(job.celery_task_id).revoke(terminate=False)
            except Exception:  # noqa: BLE001
                pass
        job.status = SearchJob.Status.CANCELADO
        job.save(update_fields=["status"])
        messages.info(request, "Busca cancelada. O worker para na proxima iteracao.")
    return redirect(job.get_absolute_url())


@login_required
@require_http_methods(["POST"])
def search_pause(request, pk: int):
    """Pausa a busca: o worker para na proxima iteracao, sem marcar falha.

    O ja feito (PDFs baixados, docs classificados) e preservado; basta Retomar.
    """
    job = get_object_or_404(SearchJob, pk=pk)
    if job.pausavel:
        if job.celery_task_id:
            try:
                AsyncResult(job.celery_task_id).revoke(terminate=False)
            except Exception:  # noqa: BLE001
                pass
        job.status = SearchJob.Status.PAUSADO
        job.fase_atual = "Pausado"
        job.save(update_fields=["status", "fase_atual"])
        messages.info(request, "Busca pausada. O worker para na proxima iteracao; use Retomar para continuar.")
    return redirect(job.get_absolute_url())


@login_required
@require_http_methods(["POST"])
def search_resume(request, pk: int):
    """Retoma uma busca pausada/cancelada/falha de onde parou.

    Re-dispara o mesmo job; a dedup e a checagem de arquivo existente pulam tudo
    que ja foi feito (downloads e classificacoes), seguindo so com os pendentes.
    """
    job = get_object_or_404(SearchJob, pk=pk)
    if not job.retomavel:
        messages.warning(request, "Esta busca nao pode ser retomada (so pausadas, canceladas ou com falha).")
        return redirect(job.get_absolute_url())

    job.status = SearchJob.Status.PENDENTE
    job.mensagem_erro = ""
    job.fase_atual = "Retomando..."
    job.mensagem_progresso = "Retomando de onde parou (o ja feito sera pulado)."
    job.finished_at = None
    job.save(update_fields=[
        "status", "mensagem_erro", "fase_atual", "mensagem_progresso", "finished_at",
    ])
    modo, ident = dispatch_search_job(job.pk)
    if modo == "celery":
        job.celery_task_id = ident
        job.save(update_fields=["celery_task_id"])
        messages.success(request, "Busca retomada no Celery. Acompanhe abaixo.")
    else:
        messages.info(request, "Busca retomada em thread local. O progresso aparece abaixo.")
    return redirect(job.get_absolute_url())
