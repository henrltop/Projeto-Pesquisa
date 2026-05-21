"""Painel publico. Apenas dados agregados e auditaveis — sem nomes, sem estado de pipeline."""
from django.db.models import Count, Max, Min
from django.shortcuts import render

from apps.dashboard.views import _construir_heatmap
from apps.documents.models import Classification, Document
from apps.reviews.models import Review


def home(request):
    # ---- KPIs agregados ----
    total_processados = Document.objects.count()
    relevantes_ia = (
        Classification.objects.filter(classificacao=Classification.Classificacao.RELEVANTE)
        .values("document").distinct().count()
    )
    aprovados_manual = Review.objects.filter(decisao=Review.Decisao.APROVADO).count()

    tipos_distintos = (
        Classification.objects.filter(classificacao=Classification.Classificacao.RELEVANTE)
        .exclude(tipo_ato="")
        .values("tipo_ato").distinct().count()
    )

    # ---- Cobertura por ano ----
    faixa = Document.objects.aggregate(min_ano=Min("ano"), max_ano=Max("ano"))
    por_ano_qs = list(
        Document.objects.values("ano").annotate(total=Count("id")).order_by("ano")
    )
    por_ano_map = {r["ano"]: r["total"] for r in por_ano_qs}

    # Completa anos faltantes entre min e max pra nao deixar furo no grafico
    cobertura = None
    if faixa["min_ano"] and faixa["max_ano"]:
        anos = list(range(faixa["min_ano"], faixa["max_ano"] + 1))
        max_v = max(por_ano_map.values()) if por_ano_map else 0

        import math
        def intensidade(v: int) -> int:
            if v <= 0 or max_v <= 0:
                return 0
            ratio = math.log1p(v) / math.log1p(max_v)
            return max(1, min(5, int(round(ratio * 5))))

        cobertura = {
            "anos": [
                {"ano": a, "total": por_ano_map.get(a, 0),
                 "intensidade": intensidade(por_ano_map.get(a, 0))}
                for a in anos
            ],
            "ano_min": faixa["min_ano"],
            "ano_max": faixa["max_ano"],
            "max_total": max_v,
            "ticks_decada": [a for a in anos if a % 10 == 0],
        }

    # ---- Heatmap tipo × ano ----
    heatmap = _construir_heatmap()

    # ---- Top tipos de ato (apenas rotulos + contagem, sem autor) ----
    top_tipos = list(
        Classification.objects.filter(classificacao=Classification.Classificacao.RELEVANTE)
        .exclude(tipo_ato="")
        .values("tipo_ato").annotate(total=Count("id")).order_by("-total")[:10]
    )

    # ---- Cadencia: relevantes por decada ----
    por_decada = {}
    if faixa["min_ano"]:
        relev_por_ano = (
            Classification.objects.filter(classificacao=Classification.Classificacao.RELEVANTE)
            .values("document__ano").annotate(total=Count("id"))
        )
        for r in relev_por_ano:
            ano = r["document__ano"]
            if not ano:
                continue
            dec = (ano // 10) * 10
            por_decada[dec] = por_decada.get(dec, 0) + r["total"]
    decadas = [{"decada": d, "total": por_decada[d]} for d in sorted(por_decada)]
    max_decada = max((d["total"] for d in decadas), default=0)

    return render(
        request,
        "public/home.html",
        {
            "total_processados": total_processados,
            "relevantes_ia": relevantes_ia,
            "aprovados_manual": aprovados_manual,
            "tipos_distintos": tipos_distintos,
            "faixa": faixa,
            "cobertura": cobertura,
            "heatmap": heatmap,
            "top_tipos": top_tipos,
            "decadas": decadas,
            "max_decada": max_decada,
        },
    )
