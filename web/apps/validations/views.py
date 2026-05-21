import csv

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Avg, Count, Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_http_methods

from .forms import BlindReviewForm, SessionConfigForm
from .models import BlindItem, BlindSession
from .sampling import criar_sessao


@login_required
def config_view(request):
    sessao_ativa = (
        BlindSession.objects
        .filter(user=request.user, status=BlindSession.Status.EM_ANDAMENTO)
        .first()
    )
    concluidas = (
        BlindSession.objects
        .filter(user=request.user, status=BlindSession.Status.CONCLUIDA)
    )

    if request.method == "POST":
        if sessao_ativa:
            messages.warning(request, "Voce ja tem uma sessao em andamento.")
            return redirect("validations:config")

        form = SessionConfigForm(request.POST)
        if form.is_valid():
            session = criar_sessao(
                user=request.user,
                tamanho=form.cleaned_data["tamanho_amostra"],
                aproveitou_avaliados=form.cleaned_data["aproveitou_avaliados"],
            )
            messages.success(
                request,
                f"Sessao criada com {session.items.count()} documentos.",
            )
            return redirect("validations:review", session_id=session.pk)
    else:
        form = SessionConfigForm()

    for s in concluidas:
        s.concordancia_pct = _concordancia_geral(s)

    return render(
        request,
        "validations/config.html",
        {
            "form": form,
            "sessao_ativa": sessao_ativa,
            "concluidas": concluidas,
            "active_nav": "validacao",
            "crumbs": [("Validacao", None)],
        },
    )


@login_required
@require_http_methods(["GET", "POST"])
def review_view(request, session_id: int):
    session = get_object_or_404(BlindSession, pk=session_id, user=request.user)

    if session.status == BlindSession.Status.CONCLUIDA:
        return redirect("validations:result", session_id=session.pk)

    item_atual = session.proximo_item
    if item_atual is None:
        session.verificar_conclusao()
        return redirect("validations:result", session_id=session.pk)

    item_revelado = None
    revelado_id = request.GET.get("revelado")
    if revelado_id:
        item_revelado = (
            session.items
            .filter(pk=revelado_id, decisao_humana__isnull=False)
            .exclude(decisao_humana="")
            .first()
        )

    if request.method == "POST":
        form = BlindReviewForm(request.POST, instance=item_atual)
        if form.is_valid():
            item = form.save(commit=False)
            item.reviewed_at = timezone.now()
            tempo = request.POST.get("tempo_avaliacao_segundos")
            if tempo and tempo.isdigit():
                item.tempo_avaliacao_segundos = int(tempo)
            item.save()

            proximo = session.proximo_item
            if proximo is None:
                session.verificar_conclusao()
                messages.success(request, "Validacao concluida!")
                return redirect("validations:result", session_id=session.pk)
            return redirect(
                f"{request.path}?revelado={item.pk}"
            )
    else:
        form = BlindReviewForm()

    total = session.items.count()
    avaliados = session.total_avaliados

    return render(
        request,
        "validations/review.html",
        {
            "session": session,
            "item": item_atual,
            "doc": item_atual.document,
            "form": form,
            "item_revelado": item_revelado,
            "avaliados": avaliados,
            "total": total,
            "progresso_pct": session.progresso_pct,
            "active_nav": "validacao",
            "crumbs": [
                ("Validacao", "validations:config"),
                (f"Sessao #{session.pk}", None),
            ],
        },
    )


def _concordancia_geral(session: BlindSession) -> int:
    agg = session.items.filter(concordancia__isnull=False).aggregate(
        total=Count("id"),
        concordantes=Count("id", filter=Q(concordancia=True)),
    )
    if agg["total"] == 0:
        return 0
    return round(100 * agg["concordantes"] / agg["total"])


def _metricas_por_categoria(session: BlindSession) -> list[dict]:
    categorias = ["relevante", "duvidoso", "irrelevante"]
    resultado = []
    for cat in categorias:
        qs = session.items.filter(categoria_ia__in=(
            ["super_relevante", "relevante"] if cat == "relevante"
            else [cat]
        ))
        total = qs.count()
        confirmados = qs.filter(resultado_binario="relevante").count()
        rejeitados = qs.filter(resultado_binario="nao_relevante").count()
        concordantes = qs.filter(concordancia=True).count()
        resultado.append({
            "categoria": cat,
            "total": total,
            "confirmados": confirmados,
            "rejeitados": rejeitados,
            "taxa_concordancia": round(100 * concordantes / total) if total else 0,
        })
    return resultado


@login_required
def result_view(request, session_id: int):
    session = get_object_or_404(BlindSession, pk=session_id, user=request.user)

    metricas = _metricas_por_categoria(session)
    concordancia_geral = _concordancia_geral(session)

    tempo_medio = session.items.filter(
        tempo_avaliacao_segundos__isnull=False,
    ).aggregate(media=Avg("tempo_avaliacao_segundos"))["media"]

    divergentes = (
        session.items
        .filter(concordancia=False)
        .select_related("document")
        .order_by("ordem")
    )

    return render(
        request,
        "validations/result.html",
        {
            "session": session,
            "metricas": metricas,
            "concordancia_geral": concordancia_geral,
            "tempo_medio": round(tempo_medio) if tempo_medio else None,
            "divergentes": divergentes,
            "total_avaliados": session.total_avaliados,
            "active_nav": "validacao",
            "crumbs": [
                ("Validacao", "validations:config"),
                (f"Sessao #{session.pk}", None),
                ("Resultado", None),
            ],
        },
    )


@login_required
def export_csv(request, session_id: int):
    session = get_object_or_404(BlindSession, pk=session_id, user=request.user)

    response = HttpResponse(content_type="text/csv; charset=utf-8")
    response["Content-Disposition"] = (
        f'attachment; filename="validacao_sessao_{session.pk}.csv"'
    )
    response.write("﻿")

    writer = csv.writer(response)
    writer.writerow([
        "ordem", "doc_id", "ano", "edicao_id", "pagina",
        "categoria_ia", "tipo_ato_ia", "justificativa_ia",
        "decisao_humana", "observacao",
        "resultado_binario", "concordancia",
        "tempo_segundos", "fonte",
    ])

    items = (
        session.items
        .select_related("document")
        .order_by("ordem")
    )
    for it in items:
        d = it.document
        writer.writerow([
            it.ordem, d.pk, d.ano, d.edicao_id, d.pagina,
            it.categoria_ia, it.tipo_ato_ia, it.justificativa_ia,
            it.decisao_humana or "", it.observacao,
            it.resultado_binario, "sim" if it.concordancia else "nao",
            it.tempo_avaliacao_segundos or "", it.fonte,
        ])

    return response
