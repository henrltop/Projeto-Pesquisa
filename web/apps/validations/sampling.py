"""Amostragem estratificada para validacao cega."""
from __future__ import annotations

import random

from django.db.models import OuterRef, Subquery
from django.utils import timezone

from apps.documents.models import Classification, Document
from apps.reviews.models import Review

from .models import BlindItem, BlindSession


def _pool_por_categoria() -> dict[str, list[int]]:
    """Retorna {categoria: [document_pks]} baseado na classificacao mais recente."""
    ultima_classe = (
        Classification.objects
        .filter(document=OuterRef("pk"))
        .order_by("-created_at")
        .values("classificacao")[:1]
    )
    docs = (
        Document.objects
        .annotate(ultima_classe=Subquery(ultima_classe))
        .exclude(ultima_classe__isnull=True)
        .values_list("pk", "ultima_classe")
    )
    pools: dict[str, list[int]] = {
        "relevante": [],
        "duvidoso": [],
        "irrelevante": [],
    }
    for pk, classe in docs:
        if classe in ("super_relevante", "relevante"):
            pools["relevante"].append(pk)
        elif classe == "duvidoso":
            pools["duvidoso"].append(pk)
        elif classe == "irrelevante":
            pools["irrelevante"].append(pk)
    return pools


def _snapshot_ia(doc_pk: int) -> dict:
    """Congela a classificacao IA mais recente de um documento."""
    c = (
        Classification.objects
        .filter(document_id=doc_pk)
        .order_by("-created_at")
        .first()
    )
    if not c:
        return {"categoria_ia": "", "tipo_ato_ia": "", "justificativa_ia": ""}
    return {
        "categoria_ia": c.classificacao,
        "tipo_ato_ia": c.tipo_ato or "",
        "justificativa_ia": c.justificativa or "",
    }


def criar_sessao(
    user,
    tamanho: int,
    aproveitou_avaliados: bool = False,
) -> BlindSession:
    session = BlindSession.objects.create(
        user=user,
        tamanho_amostra=tamanho,
        aproveitou_avaliados=aproveitou_avaliados,
    )

    por_categoria = tamanho // 3
    pools = _pool_por_categoria()
    rng = random.Random(session.pk)

    itens: list[BlindItem] = []

    for cat_key in ("relevante", "duvidoso", "irrelevante"):
        disponiveis = pools[cat_key]
        reaproveitados: list[BlindItem] = []

        if aproveitou_avaliados:
            reviews_existentes = (
                Review.objects
                .filter(document_id__in=disponiveis, revisor=user)
                .select_related("document")
            )
            for rev in reviews_existentes:
                if len(reaproveitados) >= por_categoria:
                    break
                snap = _snapshot_ia(rev.document_id)
                reaproveitados.append(BlindItem(
                    session=session,
                    document=rev.document,
                    ordem=0,
                    decisao_humana=rev.decisao,
                    observacao=rev.comentario or "[Reaproveitado de revisao anterior]",
                    reviewed_at=rev.created_at,
                    fonte=BlindItem.Fonte.REAPROVEITADO,
                    **snap,
                ))

        ja_usados = {item.document_id for item in reaproveitados}
        faltam = por_categoria - len(reaproveitados)
        candidatos = [pk for pk in disponiveis if pk not in ja_usados]

        if faltam > 0 and candidatos:
            sorteados_pks = rng.sample(candidatos, min(faltam, len(candidatos)))
            for pk in sorteados_pks:
                snap = _snapshot_ia(pk)
                reaproveitados.append(BlindItem(
                    session=session,
                    document_id=pk,
                    ordem=0,
                    fonte=BlindItem.Fonte.SORTEADO,
                    **snap,
                ))

        itens.extend(reaproveitados)

    rng.shuffle(itens)
    for i, item in enumerate(itens):
        item.ordem = i + 1

    novos = [it for it in itens if it.fonte == BlindItem.Fonte.SORTEADO]
    reaprov = [it for it in itens if it.fonte == BlindItem.Fonte.REAPROVEITADO]

    if novos:
        BlindItem.objects.bulk_create(novos)
    for item in reaprov:
        item.save()

    session.verificar_conclusao()
    return session
