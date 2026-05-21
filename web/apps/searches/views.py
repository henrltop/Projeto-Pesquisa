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
