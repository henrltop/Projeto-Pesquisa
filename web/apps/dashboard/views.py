from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.shortcuts import render

from apps.documents.models import Classification, Document
from apps.reviews.models import Review
from apps.searches.models import SearchJob


@login_required
def home(request):
    buscas_recentes = (
        SearchJob.objects.select_related("criado_por").order_by("-created_at")[:8]
    )
    total_docs = Document.objects.count()
    total_relevantes = Classification.objects.filter(
        classificacao=Classification.Classificacao.RELEVANTE,
    ).values("document").distinct().count()
    total_duvidosos_pendentes = (
        Classification.objects.filter(classificacao=Classification.Classificacao.DUVIDOSO)
        .exclude(document__reviews__isnull=False)
        .values("document").distinct().count()
    )
    total_revisados = Review.objects.count()

    por_tipo = (
        Classification.objects.filter(classificacao=Classification.Classificacao.RELEVANTE)
        .exclude(tipo_ato="")
        .values("tipo_ato").annotate(total=Count("id")).order_by("-total")[:10]
    )

    # ---- Heatmap: relevantes por (tipo_ato x ano) ----
    heatmap = _construir_heatmap()

    return render(
        request,
        "dashboard/home.html",
        {
            "buscas_recentes": buscas_recentes,
            "total_docs": total_docs,
            "total_relevantes": total_relevantes,
            "total_duvidosos_pendentes": total_duvidosos_pendentes,
            "total_revisados": total_revisados,
            "por_tipo": por_tipo,
            "heatmap": heatmap,
        },
    )


def _construir_heatmap():
    """Monta matriz (tipo_ato x ano) de contagem de relevantes.

    Normaliza o tipo_ato para uns poucos rotulos comuns e agrupa o resto como 'Outros'.
    Retorna dict: {
        tipos: ["Decreto", "Lei", ...],
        anos:  [1961, 1962, ..., 2008],
        rows:  [ { tipo, cells: [ {ano, total, intensidade(0..5)} , ... ] }, ... ],
        max_total, total_geral, ano_min, ano_max,
    }
    """
    qs = (
        Classification.objects
        .filter(classificacao=Classification.Classificacao.RELEVANTE)
        .exclude(tipo_ato="")
        .values("tipo_ato", "document__ano")
        .annotate(total=Count("id"))
    )
    if not qs:
        return None

    # normalizacao simples: primeiro token em minusculas → mapa
    MAPA = {
        "lei":        "Lei",
        "decreto":    "Decreto",
        "portaria":   "Portaria",
        "resolucao":  "Resolucao",
        "resolução":  "Resolucao",
        "parecer":    "Parecer",
        "convenio":   "Convenio",
        "convênio":   "Convenio",
    }

    def classifica(raw: str) -> str:
        t = (raw or "").strip().lower()
        for chave, label in MAPA.items():
            if t.startswith(chave):
                return label
        return "Outros"

    # matriz
    matriz: dict[str, dict[int, int]] = {}
    anos_set: set[int] = set()
    for r in qs:
        tipo = classifica(r["tipo_ato"])
        ano = r["document__ano"]
        if not ano:
            continue
        matriz.setdefault(tipo, {})
        matriz[tipo][ano] = matriz[tipo].get(ano, 0) + r["total"]
        anos_set.add(ano)

    if not anos_set:
        return None

    ano_min, ano_max = min(anos_set), max(anos_set)
    anos = list(range(ano_min, ano_max + 1))

    # ordem fixa: principais primeiro, Outros por ultimo
    ordem = ["Decreto", "Portaria", "Resolucao", "Parecer", "Lei", "Convenio", "Outros"]
    tipos = [t for t in ordem if t in matriz]

    max_total = 0
    for linha in matriz.values():
        for v in linha.values():
            if v > max_total:
                max_total = v

    def intensidade(v: int) -> int:
        if v <= 0 or max_total <= 0:
            return 0
        # 0..5 em escala log para nao achatar caudas
        import math
        ratio = math.log1p(v) / math.log1p(max_total)
        return max(1, min(5, int(round(ratio * 5))))

    rows = []
    total_geral = 0
    for tipo in tipos:
        linha = matriz.get(tipo, {})
        cells = []
        for ano in anos:
            total = linha.get(ano, 0)
            total_geral += total
            cells.append({"ano": ano, "total": total, "intensidade": intensidade(total)})
        rows.append({"tipo": tipo, "cells": cells})

    # marca de decada para o eixo x
    ticks_decada = [a for a in anos if a % 10 == 0]

    return {
        "tipos": tipos,
        "anos": anos,
        "rows": rows,
        "max_total": max_total,
        "total_geral": total_geral,
        "ano_min": ano_min,
        "ano_max": ano_max,
        "ticks_decada": ticks_decada,
    }
